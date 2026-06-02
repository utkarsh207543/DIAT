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

    new_real = u_real * cos_phase - u_imag * sin_phase
    new_imag = u_real * sin_phase + u_imag * cos_phase

    return new_real, new_imag


@njit
def saturable_absorber_jit(u_real, u_imag, Isa, modulation_depth):
    """Enhanced saturable absorber for stable mode-locking"""
    I = Isa
    intensity = u_real ** 2 + u_imag ** 2
    # More realistic SA model for stable operation
    transmission = (1 - modulation_depth) + modulation_depth / (1 + intensity / I)
    sqrt_trans = np.sqrt(transmission)

    return u_real * sqrt_trans, u_imag * sqrt_trans


@njit
def gain_saturated_jit(Pin, gss, Psat):
    """JIT-compiled gain saturation"""
    return gss / (1 + Pin / Psat)


class StableFiberLaser:
    def __init__(self):
        print("Initializing Stable Fiber Laser with Cat Ear Spectrum...")

        # Physical constants
        self.c = 299792.458  # speed of light nm/ps
        self.lx = 1030  # Central wavelength (nm) - typical for Yb fiber laser
        self.lambda_pulse = self.lx
        self.fo = self.c / self.lambda_pulse

        # Optimized parameters for stable operation
        self.nt = 2 ** 12  # Higher resolution for better spectral features
        self.time = 100  # ps - longer window for stable pulses
        self.dt = self.time / self.nt
        self.dz = 0.0005  # Smaller step size for accuracy
        self.tol = 1e-5  # Tighter tolerance for stability
        self.N_trip = 500  # More trips to reach stable state

        # Create arrays
        self.setup_arrays()

        # Enhanced SA parameters for stable mode-locking
        self.Isa = 2000  # Lower saturation intensity for better stability
        self.modulation_depth = 0.3  # 30% modulation depth

        # System parameters optimized for cat ear spectrum
        self.lambda_bw = 8  # Narrower bandwidth for cat ears
        self.PsatdBm = 23  # Lower pump power for stability

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
        # Enhanced filter for cat ear spectrum
        f_shifted = fftshift(self.f + self.fo)
        fc = self.c / self.lx
        f3dB = self.c / (self.lx) ** 2 * self.lambda_bw

        # Gaussian filter with slight asymmetry to promote cat ears
        self.filter_tf = np.exp(-((f_shifted - fc) / (f3dB / 2)) ** 2).astype(np.complex64)

        # Add spectral shaping for cat ear formation
        # Create a notch filter at center frequency
        notch_depth = 0.1  # 10% notch depth
        notch_width = f3dB / 4
        notch_filter = 1 - notch_depth * np.exp(-((f_shifted - fc) / (notch_width)) ** 2)
        self.filter_tf *= notch_filter

        # Pre-compute gain parameters
        self.gss = 10 ** (self.amf2['gssdB'] / 10)
        self.Psat = (10 ** (self.amf2['PsatdBm'] / 10)) / 1000

    def setup_fibers(self):
        """Setup fiber parameters for Yb-doped fiber laser"""
        # Yb-doped fiber parameters
        self.YbFiber = {
            'Amod': np.pi * 3.5 ** 2,  # Mode field area
            'n2': 2.6,  # Kerr coefficient
            'alpha': 0.001,  # Small loss
            'betaw': [0, 0, 22.5, 0.027],  # Dispersion coefficients for 1030nm
            'raman': 0,  # Disable Raman for simplicity
            'ssp': 0
        }
        self.YbFiber['gamma'] = 2 * np.pi * self.YbFiber['n2'] / self.lambda_pulse / self.YbFiber['Amod'] * 1e4

        # SMF for dispersion management
        self.SMF = {
            'Amod': np.pi * 5.2 ** 2,
            'n2': 2.6,
            'alpha': 0.0002,  # Very low loss
            'betaw': [0, 0, 23.0, 0.028],
            'raman': 0,
            'ssp': 0
        }
        self.SMF['gamma'] = 2 * np.pi * self.SMF['n2'] / self.lambda_pulse / self.SMF['Amod'] * 1e4

    def setup_components(self):
        """Setup optical components for stable laser"""
        # Gain fiber (Yb-doped)
        self.gain_fiber = self.YbFiber.copy()
        self.gain_fiber['L'] = 0.5e-3  # 0.5m gain fiber
        self.gain_fiber['gssdB'] = 40  # High gain
        self.gain_fiber['PsatdBm'] = self.PsatdBm
        self.gain_fiber['fbw'] = 30  # Yb gain bandwidth (THz)
        self.gain_fiber['fc'] = self.c / self.lx

        # Passive SMF sections for dispersion management
        self.smf1 = self.SMF.copy()
        self.smf1['L'] = 2e-3  # 2m SMF

        self.smf2 = self.SMF.copy()
        self.smf2['L'] = 1e-3  # 1m SMF

        # Calculate cavity parameters
        self.Length_cavity = self.gain_fiber['L'] + self.smf1['L'] + self.smf2['L']
        self.RepeatFre = self.c / 2 / self.Length_cavity
        self.gain_fiber['RepeatFre'] = self.RepeatFre

        # Output coupler (optimized for stable operation)
        self.rho_out = 0.2  # 20% output coupling

        print(f"Cavity length: {self.Length_cavity * 1000:.1f} m")
        print(f"Repetition frequency: {self.RepeatFre / 1e6:.1f} MHz")

    def linear_operator_w(self, alpha, betaw, w):
        """Linear operator in frequency domain"""
        LOP = np.full_like(w, -alpha / 2, dtype=np.complex64)

        # Include dispersion up to 3rd order
        for ii in range(min(len(betaw), 4)):
            if ii == 0:
                continue
            factorial_ii = math.factorial(ii)
            LOP = LOP - 1j * betaw[ii] * (w) ** ii / factorial_ii

        return LOP

    def laser_ip_fd_stable(self, u0, dt, dz, mod, fo):
        """Stable fiber propagation with smaller steps"""
        nt = len(u0)
        w = fftshift(2 * np.pi * np.arange(-nt / 2, nt / 2) / (dt * nt))

        u_real = u0.real.astype(np.float32)
        u_imag = u0.imag.astype(np.float32)

        propagated_length = 0

        # Pre-compute linear operator
        LOP_0 = self.linear_operator_w(mod['alpha'], mod['betaw'], w)

        # Use smaller step size for stability
        dz_fixed = min(dz * 5, mod['L'] / 10)

        while propagated_length < mod['L']:
            remaining = mod['L'] - propagated_length
            current_dz = min(dz_fixed, remaining)

            # Handle amplifier gain with spectral shaping
            if 'gssdB' in mod:
                Pin0 = (np.sum(u_real ** 2 + u_imag ** 2) * dt) * mod['RepeatFre'] * 1e-12
                gain = gain_saturated_jit(Pin0, self.gss, self.Psat)

                # Spectral gain shaping for Yb fiber
                f_gain = fftshift(self.f + fo)
                fc_gain = mod['fc']
                fbw_gain = mod['fbw']
                gain_spectrum = np.exp(-((f_gain - fc_gain) / (fbw_gain / 2)) ** 2)
                gain_array = gain * 0.5 * gain_spectrum

                LOP = LOP_0 + fftshift(gain_array)
            else:
                LOP = LOP_0

            # Split-step method
            # Linear step (half)
            u_complex = u_real + 1j * u_imag
            ufft = fft(u_complex)

            halfstep = np.exp(current_dz / 2 * LOP)
            ufft = halfstep * ufft
            u_complex = ifft(ufft)
            u_real, u_imag = u_complex.real, u_complex.imag

            # Nonlinear step
            u_real, u_imag = nonlinear_step_jit(u_real, u_imag, mod['gamma'], current_dz)

            # Linear step (half)
            u_complex = u_real + 1j * u_imag
            ufft = fft(u_complex)
            ufft = halfstep * ufft
            u_complex = ifft(ufft)
            u_real, u_imag = u_complex.real, u_complex.imag

            propagated_length += current_dz

        return u_real + 1j * u_imag

    def filter_spectral_shaping(self, ui):
        """Enhanced spectral filter for cat ear formation"""
        Ui = fft(ui)

        # Apply main filter
        Ui_filtered = Ui * self.filter_tf

        # Add additional spectral shaping
        # This creates the conditions for cat ear spectrum formation
        f_norm = (self.f + self.fo) / (self.c / self.lx)

        # Create spectral modulation that promotes cat ears
        spectral_mod = 1 + 0.05 * np.cos(2 * np.pi * (f_norm - 1) * 20)
        Ui_filtered *= fftshift(spectral_mod)

        uo = ifft(Ui_filtered)
        return uo

    def coupler_stable(self, u1i, u2i, rho):
        """Stable optical coupler"""
        rho = np.clip(rho, 0, 1)
        sqrt_rho = np.sqrt(rho)
        sqrt_1_rho = np.sqrt(1 - rho)

        u1o = sqrt_rho * u1i + 1j * sqrt_1_rho * u2i
        u2o = 1j * sqrt_1_rho * u1i + sqrt_rho * u2i
        return u1o, u2o

    def laser_sa_stable(self, u):
        """Enhanced saturable absorber for stable mode-locking"""
        u_real, u_imag = saturable_absorber_jit(u.real.astype(np.float32),
                                                u.imag.astype(np.float32),
                                                self.Isa, self.modulation_depth)
        return u_real + 1j * u_imag

    def rand_sech_stable(self, nt, time_window):
        """Generate stable initial pulse"""
        dt = time_window / nt
        t = np.arange(-time_window / 2, time_window / 2, dt)

        # Start with a well-formed sech pulse
        tfwhm = 0.5  # 500 fs pulse
        P_peak = 50  # Moderate peak power

        u0 = np.sqrt(P_peak) / np.cosh(t / tfwhm)

        # Add minimal noise for realistic startup
        np.random.seed(42)  # Fixed seed for reproducibility
        noise_level = 0.01  # Very low noise
        noise = (np.random.normal(0, noise_level, nt) +
                 1j * np.random.normal(0, noise_level, nt))
        u0 = u0 + noise

        return u0.astype(np.complex64)

    def cavity_round_trip(self, u):
        """Complete cavity round trip"""
        # Spectral filter (bandpass + shaping)
        u = self.filter_spectral_shaping(u)

        # Gain fiber
        u = self.laser_ip_fd_stable(u, self.dt, self.dz, self.gain_fiber, self.fo)

        # SMF section 1
        u = self.laser_ip_fd_stable(u, self.dt, self.dz, self.smf1, self.fo)

        # Saturable absorber
        u = self.laser_sa_stable(u)

        # SMF section 2
        u = self.laser_ip_fd_stable(u, self.dt, self.dz, self.smf2, self.fo)

        # Output coupler
        zeros = np.zeros_like(u)
        u, uout = self.coupler_stable(u, zeros, self.rho_out)

        return u, uout

    def run_simulation(self):
        """Run stable fiber laser simulation"""
        print("Starting Stable Fiber Laser Simulation...")

        # Initialize with stable pulse
        u0 = self.rand_sech_stable(self.nt, self.time)
        u = u0.copy()

        # Storage for analysis
        store_every = 10
        n_stored = self.N_trip // store_every
        spec_z = np.zeros((n_stored, self.nt), dtype=np.complex64)
        u_z = np.zeros((n_stored, self.nt), dtype=np.complex64)

        convergence_reached = False
        store_idx = 0

        # Track stability metrics
        powers = []
        energies = []
        pulse_widths = []

        print("Building up to stable operation...")

        for ii in range(self.N_trip):
            # Complete round trip
            u, uout = self.cavity_round_trip(u)

            # Calculate metrics
            power = np.max(np.abs(uout) ** 2)
            energy = self.dt * np.sum(np.abs(u) ** 2)
            powers.append(power)
            energies.append(energy)

            # Calculate pulse width (FWHM)
            intensity = np.abs(uout) ** 2
            max_intensity = np.max(intensity)
            half_max = max_intensity / 2
            indices = np.where(intensity >= half_max)[0]
            if len(indices) > 1:
                pulse_width = (indices[-1] - indices[0]) * self.dt
            else:
                pulse_width = self.dt
            pulse_widths.append(pulse_width)

            # Print progress
            if ii % 50 == 0:
                print(f'Round Trip = {ii + 1}')
                print(f'  Peak Power = {power:.3f} W')
                print(f'  Pulse Energy = {energy:.3f} pJ')
                print(f'  Pulse Width = {pulse_width:.3f} ps')

            # Store results
            if ii % store_every == 0 and store_idx < n_stored:
                spec = fftshift(fft(uout))
                specnorm = spec * np.conj(spec)
                specnorm = specnorm / np.max(specnorm)

                spec_z[store_idx, :] = specnorm
                u_z[store_idx, :] = uout
                store_idx += 1

            # Check for stability (last 50 round trips)
            if ii > 100 and ii % 25 == 0:
                if len(powers) >= 50:
                    recent_powers = powers[-50:]
                    power_std = np.std(recent_powers) / np.mean(recent_powers)
                    if power_std < 0.01:  # 1% stability
                        print(f'Stable operation achieved at round trip {ii + 1}!')
                        print(f'Power stability: {power_std * 100:.2f}%')
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
            'powers': powers,
            'energies': energies,
            'pulse_widths': pulse_widths
        }

    def plot_results(self, results):
        """Plot comprehensive results including cat ear spectrum"""
        uout = results['uout']
        u_z = results['u_z']
        spec_z = results['spec_z']
        t = results['t']
        f = results['f']
        fo = results['fo']
        c = results['c']
        final_round = results['final_round']
        powers = results['powers']
        pulse_widths = results['pulse_widths']

        # Calculate final pulse properties
        Eout = np.abs(uout) ** 2
        energy = results['dt'] * np.sum(Eout)

        # Create comprehensive plots
        plt.figure(figsize=(18, 12))

        # 1. Final pulse shape
        plt.subplot(3, 4, 1)
        plt.plot(t, Eout, 'b-', linewidth=2)
        plt.grid(True)
        plt.xlabel('Time (ps)')
        plt.ylabel('Power (W)')
        plt.title('Stable Pulse Shape')

        # 2. Cat ear spectrum
        spec = fftshift(fft(uout))
        specnorm = np.abs(spec) ** 2
        specnorm = specnorm / np.max(specnorm)
        lambda_plot = c / (f + fo)

        plt.subplot(3, 4, 2)
        plt.plot(lambda_plot, 10 * np.log10(specnorm + 1e-10), 'r-', linewidth=2)
        plt.grid(True)
        plt.xlabel('Wavelength (nm)')
        plt.ylabel('Spectrum (dB)')
        plt.title('Cat Ear Spectrum')
        plt.ylim([-40, 5])

        # 3. Linear spectrum
        plt.subplot(3, 4, 3)
        plt.plot(lambda_plot, specnorm, 'g-', linewidth=2)
        plt.grid(True)
        plt.xlabel('Wavelength (nm)')
        plt.ylabel('Normalized Spectrum')
        plt.title('Linear Spectrum')

        # 4. Power evolution
        plt.subplot(3, 4, 4)
        plt.plot(powers, 'b-', linewidth=1)
        plt.grid(True)
        plt.xlabel('Round Trip')
        plt.ylabel('Peak Power (W)')
        plt.title('Power Stability')

        # 5. Pulse width evolution
        plt.subplot(3, 4, 5)
        plt.plot(pulse_widths, 'g-', linewidth=1)
        plt.grid(True)
        plt.xlabel('Round Trip')
        plt.ylabel('Pulse Width (ps)')
        plt.title('Pulse Width Evolution')

        # 6. Field evolution
        plt.subplot(3, 4, 6)
        if len(u_z) > 1:
            plt.pcolormesh(t, np.arange(len(u_z)), np.abs(u_z) ** 2, shading='auto')
            plt.colorbar(label='Power (W)')
        plt.xlabel('Time (ps)')
        plt.ylabel('Round Trip')
        plt.title('Temporal Evolution')

        # 7. Spectral evolution
        plt.subplot(3, 4, 7)
        if len(spec_z) > 1:
            plt.pcolormesh(lambda_plot, np.arange(len(spec_z)),
                           10 * np.log10(spec_z.real + 1e-10), shading='auto')
            plt.colorbar(label='Spectrum (dB)')
        plt.xlabel('Wavelength (nm)')
        plt.ylabel('Round Trip')
        plt.title('Spectral Evolution')

        # 8. Autocorrelation
        AC = correlate(Eout, Eout, mode='full')
        AC = AC / np.max(AC)
        time_delay = np.arange(-len(t) + 1, len(t)) * results['dt']

        plt.subplot(3, 4, 8)
        plt.plot(time_delay, AC, 'purple', linewidth=2)
        plt.xlabel('Time Delay (ps)')
        plt.ylabel('Autocorrelation')
        plt.title('Pulse Autocorrelation')
        plt.grid(True)

        # 9. Phase
        phase = np.unwrap(np.angle(uout))
        plt.subplot(3, 4, 9)
        plt.plot(t, phase, 'orange', linewidth=2)
        plt.xlabel('Time (ps)')
        plt.ylabel('Phase (rad)')
        plt.title('Pulse Phase')
        plt.grid(True)

        # 10. Chirp
        chirp = np.gradient(phase) / (2 * np.pi * results['dt'])
        plt.subplot(3, 4, 10)
        plt.plot(t, chirp, 'brown', linewidth=2)
        plt.xlabel('Time (ps)')
        plt.ylabel('Chirp (THz)')
        plt.title('Instantaneous Frequency')
        plt.grid(True)

        # 11. Stability metrics
        plt.subplot(3, 4, 11)
        if len(powers) >= 50:
            recent_powers = powers[-50:]
            stability = np.std(recent_powers) / np.mean(recent_powers) * 100
            plt.text(0.1, 0.8, f'Power Stability: {stability:.2f}%', transform=plt.gca().transAxes, fontsize=12)
            plt.text(0.1, 0.6, f'Final Power: {powers[-1]:.1f} W', transform=plt.gca().transAxes, fontsize=12)
            plt.text(0.1, 0.4, f'Pulse Width: {pulse_widths[-1]:.3f} ps', transform=plt.gca().transAxes, fontsize=12)
            plt.text(0.1, 0.2, f'Rep Rate: {results["RepeatFre"] / 1e6:.1f} MHz', transform=plt.gca().transAxes,
                     fontsize=12)
        plt.title('Laser Parameters')
        plt.axis('off')

        # 12. Cat ear detail
        plt.subplot(3, 4, 12)
        # Zoom in on cat ear features
        center_idx = np.argmin(np.abs(lambda_plot - self.lx))
        zoom_range = 100  # points around center
        zoom_lambda = lambda_plot[center_idx - zoom_range:center_idx + zoom_range]
        zoom_spec = specnorm[center_idx - zoom_range:center_idx + zoom_range]

        plt.plot(zoom_lambda, zoom_spec, 'r-', linewidth=2)
        plt.grid(True)
        plt.xlabel('Wavelength (nm)')
        plt.ylabel('Normalized Spectrum')
        plt.title('Cat Ear Detail')

        plt.tight_layout()
        plt.show()

        # Print comprehensive statistics
        print(f"\n=== Stable Fiber Laser Results ===")
        print(f"Operation: {'Stable' if final_round < results['final_round'] else 'Converged'}")
        print(f"Final round trip: {final_round}")
        print(f"Final peak power: {np.max(Eout):.3f} W")
        print(f"Final pulse energy: {energy:.3f} pJ")
        print(f"Final pulse width: {pulse_widths[-1]:.3f} ps")
        print(f"Repetition frequency: {results['RepeatFre'] / 1e6:.1f} MHz")

        if len(powers) >= 50:
            recent_powers = powers[-50:]
            stability = np.std(recent_powers) / np.mean(recent_powers) * 100
            print(f"Power stability (last 50 trips): {stability:.2f}%")

        # Analyze cat ear features
        spec_db = 10 * np.log10(specnorm + 1e-10)
        peaks = []
        for i in range(1, len(spec_db) - 1):
            if spec_db[i] > spec_db[i - 1] and spec_db[i] > spec_db[i + 1] and spec_db[i] > -20:
                peaks.append(i)

        if len(peaks) >= 2:
            print(f"Cat ear features detected: {len(peaks)} spectral peaks")
            peak_wavelengths = lambda_plot[peaks]
            print(f"Peak wavelengths: {peak_wavelengths}")


def main():
    """Main function for stable fiber laser simulation"""
    # Create simulation instance
    laser = StableFiberLaser()

    # Run simulation
    start_time = time.time()
    results = laser.run_simulation()
    end_time = time.time()

    print(f"Simulation completed in {end_time - start_time:.2f} seconds")

    # Plot comprehensive results
    laser.plot_results(results)

    return results


if __name__ == "__main__":
    results = main()