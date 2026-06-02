import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, ifft, fftshift, ifftshift
from scipy.signal import correlate
import math
import time
from numba import jit, njit
import warnings

warnings.filterwarnings('ignore')


# JIT-compiled functions for maximum CPU speed
@njit
def nonlinear_step_jit(u_real, u_imag, gamma, dz):
    """JIT-compiled nonlinear step"""
    u_abs_sq = u_real ** 2 + u_imag ** 2
    phase = gamma * u_abs_sq * dz
    cos_phase = np.cos(phase)
    sin_phase = np.sin(phase)

    # Apply nonlinear phase: u * exp(i * phase)
    new_real = u_real * cos_phase - u_imag * sin_phase
    new_imag = u_real * sin_phase + u_imag * cos_phase

    return new_real, new_imag


@njit
def linear_step_jit(ufft_real, ufft_imag, LOP_real, LOP_imag):
    """JIT-compiled linear step"""
    # Multiply by exp(LOP): (a+bi) * exp(c+di) = (a+bi) * (cos(d)*exp(c) + i*sin(d)*exp(c))
    exp_real = np.exp(LOP_real)
    cos_imag = np.cos(LOP_imag)
    sin_imag = np.sin(LOP_imag)

    exp_LOP_real = exp_real * cos_imag
    exp_LOP_imag = exp_real * sin_imag

    # Complex multiplication
    result_real = ufft_real * exp_LOP_real - ufft_imag * exp_LOP_imag
    result_imag = ufft_real * exp_LOP_imag + ufft_imag * exp_LOP_real

    return result_real, result_imag


@njit
def saturable_absorber_jit(u_real, u_imag, Isa):
    """JIT-compiled saturable absorber"""
    I = Isa / 5
    intensity = u_real ** 2 + u_imag ** 2
    transmission = 0.01 + intensity / I / (1 + intensity / I)
    sqrt_trans = np.sqrt(transmission)

    return u_real * sqrt_trans, u_imag * sqrt_trans


@njit
def gain_saturated_jit(Pin, gss, Psat):
    """JIT-compiled gain saturation"""
    return gss / (1 + Pin / Psat)


class FiberLaserSimulationCPU:
    def __init__(self):
        print("Initializing CPU-Optimized Fiber Laser Simulation...")

        # Physical constants
        self.c = 299792.458  # speed of light nm/ps
        self.lx = 1050  # wavelength in nm
        self.lambda_pulse = self.lx
        self.fo = self.c / self.lambda_pulse  # central pulse frequency (THz)

        # Optimized numerical parameters
        self.nt = 2 ** 11  # 2048 points
        self.time = 80  # ps
        self.dt = self.time / self.nt
        self.dz = 0.002  # Larger step size for speed
        self.tol = 1e-4  # Relaxed tolerance
        self.N_trip = 200  # Number of trips

        # Create arrays
        self.setup_arrays()

        # SA parameters
        self.Isa = 5000  # saturation intensity (W)

        # System parameters
        self.lambda_bw = 11  # bandwidth in nm
        self.PsatdBm = 26  # Pump power in dBm

        # Initialize fiber parameters
        self.setup_fibers()
        self.setup_components()

        # Pre-compute arrays
        self.precompute_arrays()

        print("Initialization complete!")

    def setup_arrays(self):
        """Setup time and frequency arrays"""
        self.t = np.arange(-self.time / 2, self.time / 2, self.dt, dtype=np.float32)
        self.df = 1 / (self.nt * self.dt)
        self.f = np.arange(-(self.nt / 2) * self.df, (self.nt / 2) * self.df, self.df, dtype=np.float32)
        self.lambda_vec = self.c / (self.f + self.c / self.lambda_pulse)
        self.w = 2 * np.pi * self.f

    def precompute_arrays(self):
        """Pre-compute frequently used arrays"""
        # Pre-compute filter transfer function
        f_shifted = fftshift(self.f + self.fo)
        fc = self.c / self.lx
        f3dB = self.c / (self.lx) ** 2 * self.lambda_bw
        self.filter_tf = np.exp(-((f_shifted - fc) / (f3dB / 2)) ** 2).astype(np.complex64)

        # Pre-compute gain parameters
        self.gss = 10 ** (self.amf2['gssdB'] / 10)
        self.Psat = (10 ** (self.amf2['PsatdBm'] / 10)) / 1000

    def setup_fibers(self):
        """Setup fiber parameters"""
        self.F10125 = {
            'Amod': np.pi * 5.25 ** 2,
            'n2': 2.6,
            'alpha': 0,
            'betaw': [0, 0, 20.1814, 36.8057e-3],
            'raman': 0,  # Disable Raman for speed
            'ssp': 0
        }
        self.F10125['gamma'] = 2 * np.pi * self.F10125['n2'] / self.lambda_pulse / self.F10125['Amod'] * 1e4

    def setup_components(self):
        """Setup optical components"""
        # SMF components
        self.smf7 = self.F10125.copy()
        self.smf7['L'] = 0.003

        self.smf8 = self.F10125.copy()
        self.smf8['L'] = 0.001

        # Amplifier
        self.amf2 = self.F10125.copy()
        self.amf2['L'] = 0.001
        self.amf2['gssdB'] = 37.5
        self.amf2['PsatdBm'] = self.PsatdBm
        self.amf2['fbw'] = self.c / (self.lx) ** 2 * 80
        self.amf2['fc'] = self.c / self.lx

        # Calculate cavity parameters
        self.Length_cavity = self.smf7['L'] + self.smf8['L'] + self.amf2['L']
        self.RepeatFre = self.c / 2 / self.Length_cavity
        self.amf2['RepeatFre'] = self.RepeatFre

        # Coupler parameters
        self.rho_out2 = 0.23

    def linear_operator_w(self, alpha, betaw, w):
        """Linear operator in frequency domain"""
        LOP = np.full_like(w, -alpha / 2, dtype=np.complex64)

        # Vectorized dispersion calculation
        for ii in range(min(len(betaw), 4)):
            if ii == 0:
                continue
            factorial_ii = math.factorial(ii)
            LOP = LOP - 1j * betaw[ii] * (w) ** ii / factorial_ii

        return LOP

    def laser_ip_fd_fast(self, u0, dt, dz, mod, fo):
        """Fast fiber propagation using optimized split-step"""
        nt = len(u0)
        w = fftshift(2 * np.pi * np.arange(-nt / 2, nt / 2) / (dt * nt))

        # Convert to real/imag for JIT functions
        u_real = u0.real.astype(np.float32)
        u_imag = u0.imag.astype(np.float32)

        propagated_length = 0

        # Pre-compute linear operator
        LOP_0 = self.linear_operator_w(mod['alpha'], mod['betaw'], w)

        # Use larger, fixed step size
        dz_fixed = min(dz * 30, mod['L'] / 3)

        while propagated_length < mod['L']:
            remaining = mod['L'] - propagated_length
            current_dz = min(dz_fixed, remaining)

            # Handle amplifier gain
            if 'gssdB' in mod:
                Pin0 = (np.sum(u_real ** 2 + u_imag ** 2) * dt) * mod['RepeatFre'] * 1e-12
                gain = gain_saturated_jit(Pin0, self.gss, self.Psat)
                gain_array = np.full_like(w, gain * 0.5, dtype=np.complex64)
                LOP = LOP_0 + fftshift(gain_array)
            else:
                LOP = LOP_0

            # Split-step method with JIT optimization
            # Linear step (half)
            u_complex = u_real + 1j * u_imag
            ufft = fft(u_complex)

            halfstep = np.exp(current_dz / 2 * LOP)
            ufft = halfstep * ufft
            u_complex = ifft(ufft)
            u_real, u_imag = u_complex.real, u_complex.imag

            # Nonlinear step (JIT optimized)
            u_real, u_imag = nonlinear_step_jit(u_real, u_imag, mod['gamma'], current_dz)

            # Linear step (half)
            u_complex = u_real + 1j * u_imag
            ufft = fft(u_complex)
            ufft = halfstep * ufft
            u_complex = ifft(ufft)
            u_real, u_imag = u_complex.real, u_complex.imag

            propagated_length += current_dz

        return u_real + 1j * u_imag

    def filter_gauss_fast(self, ui):
        """Fast Gaussian filter"""
        Ui = fft(ui)
        uo = ifft(Ui * self.filter_tf)
        return uo

    def coupler_fast(self, u1i, u2i, rho):
        """Fast optical coupler"""
        rho = np.clip(rho, 0, 1)
        sqrt_rho = np.sqrt(rho)
        sqrt_1_rho = np.sqrt(1 - rho)

        u1o = sqrt_rho * u1i + 1j * sqrt_1_rho * u2i
        u2o = 1j * sqrt_1_rho * u1i + sqrt_rho * u2i
        return u1o, u2o

    def laser_sa_fast(self, u):
        """Fast saturable absorber using JIT"""
        u_real, u_imag = saturable_absorber_jit(u.real.astype(np.float32),
                                                u.imag.astype(np.float32),
                                                self.Isa)
        return u_real + 1j * u_imag

    def rand_sech(self, nt, time_window):
        """Generate random sech pulse"""
        dt = time_window / nt
        t = np.arange(-time_window / 2, time_window / 2, dt)

        tfwhm = time_window / 8
        P_peak = 100

        u0 = np.sqrt(P_peak) / np.cosh(t / tfwhm)

        # Add noise
        np.random.seed(0)
        noise_level = 0.1
        noise = (np.random.normal(0, noise_level, nt) +
                 1j * np.random.normal(0, noise_level, nt))
        u0 = u0 + noise

        return u0.astype(np.complex64)

    def design_sa_fast(self, u):
        """Fast SA ring laser design"""
        # BPF
        u = self.filter_gauss_fast(u)

        # SMF7
        u = self.laser_ip_fd_fast(u, self.dt, self.dz, self.smf7, self.fo)

        # AMF2 (amplifier)
        u = self.laser_ip_fd_fast(u, self.dt, self.dz, self.amf2, self.fo)

        # SMF8
        u = self.laser_ip_fd_fast(u, self.dt, self.dz, self.smf8, self.fo)

        # SA (Saturable Absorber)
        u = self.laser_sa_fast(u)

        # Output Coupler
        zeros = np.zeros_like(u)
        u, uout = self.coupler_fast(u, zeros, self.rho_out2)

        return u, uout

    def run_simulation(self):
        """Optimized main simulation loop"""
        print("Starting CPU-Optimized Fiber Laser Simulation...")

        # Initialize
        u0 = self.rand_sech(self.nt, self.time)
        u = u0.copy()

        # Storage (reduced for memory efficiency)
        store_every = 5
        n_stored = self.N_trip // store_every
        spec_z = np.zeros((n_stored, self.nt), dtype=np.complex64)
        u_z = np.zeros((n_stored, self.nt), dtype=np.complex64)

        convergence_reached = False
        store_idx = 0

        # Progress tracking
        powers = []

        for ii in range(self.N_trip):
            # Run SA design
            u, uout = self.design_sa_fast(u)

            # Calculate power (using abs instead of complex operations)
            power = np.max(np.abs(uout) ** 2)  # This works with complex numbers
            energy = self.dt * np.sum(np.abs(u) ** 2)
            powers.append(power)

            # Print progress
            if ii % 25 == 0:
                print(f'Round Trip = {ii + 1}, Peak Power = {power:.3f} W, Energy = {energy:.3f} pJ')

            # Store results
            if ii % store_every == 0 and store_idx < n_stored:
                spec = fftshift(fft(uout))
                specnorm = spec * np.conj(spec)
                specnorm = specnorm / np.max(specnorm)

                spec_z[store_idx, :] = specnorm
                u_z[store_idx, :] = uout
                store_idx += 1

            # Convergence check
            if ii > 30 and ii % 15 == 0:
                if len(powers) >= 2:
                    rel_change = abs(powers[-1] - powers[-2]) / powers[-2]
                    if rel_change < 0.001:
                        print('Convergence reached!')
                        convergence_reached = True
                        break

        final_round = ii + 1 if convergence_reached else self.N_trip

        return {
            'u_z': u_z[:store_idx, :],
            'spec_z': spec_z[:store_idx, :],
            'uout': uout,
            'final_round': final_round,
            't': self.t,
            'f': self.f,
            'lambda': self.lambda_vec,
            'fo': self.fo,
            'c': self.c,
            'dt': self.dt,
            'RepeatFre': self.RepeatFre,
            'powers': powers
        }

    def plot_results(self, results):
        """Plot simulation results"""
        uout = results['uout']
        u_z = results['u_z']
        spec_z = results['spec_z']
        t = results['t']
        f = results['f']
        fo = results['fo']
        c = results['c']
        final_round = results['final_round']
        powers = results['powers']

        # Calculate pulse properties
        Eout = np.abs(uout) ** 2
        energy = results['dt'] * np.sum(Eout)

        # Create plots
        plt.figure(figsize=(15, 10))

        plt.subplot(2, 3, 1)
        plt.plot(t, Eout)
        plt.grid(True)
        plt.xlabel('t (ps)')
        plt.ylabel('|u(z,t)|² (W)')
        plt.title(f'Pulse Shape ({results["RepeatFre"] / 1e6:.1f}MHz)')

        # Output spectrum
        spec = fftshift(fft(uout))
        specnorm = np.abs(spec) ** 2
        specnorm = specnorm / np.max(specnorm)

        plt.subplot(2, 3, 2)
        lambda_plot = c / (f + fo)
        plt.plot(lambda_plot, specnorm)
        plt.grid(True)
        plt.xlabel('λ (nm)')
        plt.ylabel('Normalized Spectrum (a.u.)')
        plt.title('Output Spectrum')

        # Field evolution
        plt.subplot(2, 3, 3)
        plt.pcolormesh(t, np.arange(len(u_z)), np.abs(u_z) ** 2, shading='auto')
        plt.colorbar(label='|u(z,t)|² (W)')
        plt.xlabel('t (ps)')
        plt.ylabel('Stored Round Trip')
        plt.title('Field Evolution')

        # Spectrum evolution
        plt.subplot(2, 3, 4)
        plt.pcolormesh(lambda_plot, np.arange(len(spec_z)),
                       spec_z.real, shading='auto')
        plt.colorbar(label='Spectrum (a.u.)')
        plt.xlabel('λ (nm)')
        plt.ylabel('Stored Round Trip')
        plt.title('Spectrum Evolution')

        # Power evolution
        plt.subplot(2, 3, 5)
        plt.plot(powers)
        plt.xlabel('Round Trip')
        plt.ylabel('Peak Power (W)')
        plt.title('Power Evolution')
        plt.grid(True)

        # Autocorrelation
        AC = correlate(Eout, Eout, mode='full')
        AC = AC / np.max(AC)
        time_delay = np.arange(-len(t) + 1, len(t)) * results['dt']

        plt.subplot(2, 3, 6)
        plt.plot(time_delay, AC)
        plt.xlabel('Time Delay (ps)')
        plt.ylabel('AC Trace (a.u.)')
        plt.title('Autocorrelation')
        plt.grid(True)

        plt.tight_layout()
        plt.show()

        # Print final statistics
        print(f"\n=== CPU-Optimized Simulation Results ===")
        print(f"Converged after {final_round} round trips")
        print(f"Final peak power: {np.max(Eout):.3f} W")
        print(f"Final pulse energy: {energy:.3f} pJ")
        print(f"Repetition frequency: {results['RepeatFre'] / 1e6:.1f} MHz")


def main():
    """Main function"""
    # Create simulation instance
    sim = FiberLaserSimulationCPU()

    # Run simulation
    start_time = time.time()
    results = sim.run_simulation()
    end_time = time.time()

    print(f"Simulation completed in {end_time - start_time:.2f} seconds")

    # Plot results
    sim.plot_results(results)

    return results


if __name__ == "__main__":
    # Install numba if not available: pip install numba
    results = main()