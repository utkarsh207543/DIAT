# Fiber Laser Simulator: Full Cavity Model with Noise

import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, ifft, fftshift
from scipy.signal import correlate
import os
import scipy.io as sio
import pandas as pd

# --- Constants ---
c = 299792.458
lx = 1050
lambda_pulse = lx
fo = c / lambda_pulse

# --- Numerical Grid ---
nt = 2 ** 12
time_window = 120
dt = time_window / nt
t = np.linspace(-time_window / 2, time_window / 2 - dt, nt)
df = 1 / (nt * dt)
f = np.linspace(-nt / 2 * df, (nt / 2 - 1) * df, nt)
dz = 0.00001
tol = 1e-7
N_trip = 1000


# --- Modules ---
def rand_sech(nt, time_window, beta2=20.1814, gamma=1.8317):
    tfwhm = time_window / 4
    P_peak = 2 * abs(beta2) / (gamma * tfwhm ** 2)
    pulse = np.sqrt(P_peak) / np.cosh(t / tfwhm)
    np.random.seed(0)
    noise = np.abs(np.random.normal(0, np.sqrt(10 ** (25 / 10)), nt))
    return noise * pulse


def xcorr_normal(x, y, lag):
    out = correlate(x, y, mode='full')
    out = out / ((np.sqrt(np.sum(x ** 2) * np.sum(y ** 2))) / len(x) ** 2)
    mid = len(out) // 2
    return out[mid - lag:mid + lag + 1]


def filter_BPF(ui, mod, fo, df):
    Ui = fft(ui)
    N = len(Ui)
    f = fftshift(np.linspace(-N / 2 * df, (N / 2 - 1) * df, N) + fo)
    lambda_vals = c / (f + fo)
    delta_phi = (2 * np.pi / lambda_vals * 1e9) * mod['L'] * mod['bf']
    Tf = np.cos(delta_phi / 2) ** 2
    return ifft(Ui * Tf)


def LASER_IP_FD(u0, dt, dz, fiber, fo, tol):
    nt = len(u0)
    dz_step = dz
    z_total = fiber['L']
    nz = int(np.ceil(z_total / dz_step))
    dz_step = z_total / nz

    gamma = fiber['gamma']
    alpha = fiber['alpha']
    beta2 = fiber['betaw'][2]
    beta3 = fiber['betaw'][3]

    w = 2 * np.pi * np.fft.fftfreq(nt, dt)
    u = u0.copy()

    for _ in range(nz):
        Lw = -1j * (0.5 * beta2 * w ** 2 + (1 / 6) * beta3 * w ** 3) - alpha / 2
        u_freq = fft(u) * np.exp(Lw * dz_step / 2)
        u = ifft(u_freq)
        NL = -1j * gamma * np.abs(u) ** 2
        u = u * np.exp(NL * dz_step)
        u_freq = fft(u) * np.exp(Lw * dz_step / 2)
        u = ifft(u_freq)

    return u, nz, {}


def LASER_SA(u_t, Isa):
    intensity = np.abs(u_t) ** 2
    transmission = 1 / (1 + intensity / Isa)
    return u_t * np.sqrt(transmission)


def AmpSimpNoise(Ein, L, gssdB, PsatdBm, NF=5.0, f_THz=193.1):
    h = 6.6261e-34
    f = f_THz * 1e12
    Gss = 10 ** (gssdB / 10)
    Psat = 10 ** (PsatdBm / 10) * 1e-3
    Pin = np.mean(np.abs(Ein) ** 2)
    G = Gss
    for _ in range(1000):
        G_new = Gss * np.exp(-(G - 1) * Pin / Psat)
        if abs(G_new - G) < 1e-4:
            break
        G = G_new
    gain = G
    Egain = np.sqrt(np.exp(np.log(gain) * L)) * Ein
    Bsim = 1 / dt
    FigNoise = 10 ** (NF / 10)
    nsp = (FigNoise * gain - 1) / (2 * (gain - 1))
    Pase = h * f * nsp * (gain - 1) * Bsim
    noise = (np.random.randn(len(Egain)) + 1j * np.random.randn(len(Egain))) * np.sqrt(Pase / 2)
    return Egain + noise, np.log(gain)


def coupler(u1i, u2i, rho):
    rho = np.clip(rho, 0, 1)
    return np.sqrt(rho) * u1i + 1j * np.sqrt(1 - rho) * u2i, \
           1j * np.sqrt(1 - rho) * u1i + np.sqrt(rho) * u2i


# --- Fiber and Cavity Parameters ---
fiber_smf = {'L': 0.005, 'gamma': 1.8, 'alpha': 0.0, 'betaw': [0, 0, 20.1814, 0.0368]}
fiber_post_amp = {'L': 0.001, 'gamma': 1.8, 'alpha': 0.0, 'betaw': [0, 0, 20.1814, 0.0368]}
amp_params = {'L': 0.001, 'gssdB': 37.5, 'PsatdBm': 26}
mod_bpf = {'L': 0.001, 'bf': 1e-3}
Isa = 5000
rho_out = 0.4

# --- Simulation ---
u = rand_sech(nt, time_window)
spec_z = np.zeros((N_trip, nt))
u_z = np.zeros((N_trip, nt))
dstop = False

for ii in range(N_trip):
    print(f"Round Trip {ii + 1}")
    u = filter_BPF(u, mod_bpf, fo, df)
    u, _, _ = LASER_IP_FD(u, dt, dz, fiber_smf, fo, tol)
    u, _ = AmpSimpNoise(u, **amp_params)
    u, _, _ = LASER_IP_FD(u, dt, dz, fiber_post_amp, fo, tol)
    u = LASER_SA(u, Isa)
    u, uout = coupler(u, 0, rho_out)
    spec = fftshift(fft(uout))
    specnorm = np.abs(spec) ** 2 / np.max(np.abs(spec) ** 2)
    spec_z[ii, :] = specnorm
    u_z[ii, :] = np.abs(uout) ** 2
    if ii > 5:
        corr = xcorr_normal(spec_z[ii, :], spec_z[ii - 1, :], nt // 8)
        if np.max(corr) > 0.99999:
            print("Convergence achieved.")
            break

# --- Plots ---
plt.figure(1)
plt.plot(t, np.abs(uout) ** 2)
plt.title("Final Pulse Shape")
plt.xlabel("t (ps)")
plt.ylabel("|u(t)|^2 (W)")
plt.grid(True)

plt.figure(2)
plt.plot(c / (f + fo), specnorm)
plt.title("Final Spectrum")
plt.xlabel("Wavelength (nm)")
plt.ylabel("Normalized Spectrum")
plt.grid(True)

plt.figure(3)
plt.imshow(u_z[:ii + 1, :], aspect='auto', extent=[t[0], t[-1], 1, ii + 1], origin='lower')
plt.title("Pulse Evolution")
plt.xlabel("t (ps)")
plt.ylabel("Round Trip")
plt.colorbar(label='|u(t)|^2 (W)')

plt.figure(4)
plt.imshow(spec_z[:ii + 1, :], aspect='auto', extent=[c / (f[-1] + fo), c / (f[0] + fo), 1, ii + 1], origin='lower')
plt.title("Spectrum Evolution")
plt.xlabel("Wavelength (nm)")
plt.ylabel("Round Trip")
plt.colorbar(label='Normalized Spectrum')
plt.tight_layout()
plt.show()

# --- Save Results ---
save_dir = "ring_laser_results"
os.makedirs(save_dir, exist_ok=True)
np.save(os.path.join(save_dir, "pulse_profile.npy"), np.abs(uout) ** 2)
np.save(os.path.join(save_dir, "spectrum.npy"), specnorm)
np.save(os.path.join(save_dir, "evolution_pulse.npy"), u_z[:ii + 1, :])
np.save(os.path.join(save_dir, "evolution_spectrum.npy"), spec_z[:ii + 1, :])

pd.DataFrame({'t_ps': t, 'pulse_W': np.abs(uout) ** 2}).to_csv(os.path.join(save_dir, 'pulse_profile.csv'), index=False)
pd.DataFrame({'lambda_nm': c / (f + fo), 'spectrum_a.u.': specnorm}).to_csv(os.path.join(save_dir, 'spectrum.csv'),
                                                                            index=False)

sio.savemat(os.path.join(save_dir, "ring_laser_data.mat"), {
    't': t,
    'lambda': c / (f + fo),
    'pulse_profile': np.abs(uout) ** 2,
    'spectrum': specnorm,
    'pulse_evolution': u_z[:ii + 1, :],
    'spectrum_evolution': spec_z[:ii + 1, :],
    'N_roundtrips': ii + 1
})
