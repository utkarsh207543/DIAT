# EDFA small-signal simulator (two-level model with wavelength-dependent cross sections)
# -----------------------------------------------------------------------------
# What this script does
# - Models a lumped EDFA in the small-signal regime using a steady-state two-level rate model
# - Uses wavelength-dependent emission/absorption cross-sections (sum of Gaussians) to form a realistic gain spectrum
# - Computes population inversion from pump photon flux (980 nm or 1480 nm pumping)
# - Computes small-signal gain G(λ) = exp{ [Γ_s (σ_e(λ) N2 − σ_a(λ) N1)] L }
# - Computes spontaneous-emission factor n_sp(λ) = σ_e(λ) N2 / (σ_e(λ) N2 − σ_a(λ) N1)
# - Computes noise figure NF(λ) = 10 log10( 2 n_sp (1 + 1/G) ), approximates → 10 log10(2 n_sp) for G≫1
# - Forms input spectrum as a Gaussian with given center wavelength and FWHM and total input power
# - Produces plots: Gain vs λ, Noise Figure vs λ, Input/Output Spectra vs λ, ASE spectral density vs λ
# - Outputs a summary table per-wavelength and key integrated figures
#
# Notes
# - This is a *small-signal* model (no gain saturation due to the signal; pump depletion is ignored).
# - For 980-nm pumping, stimulated emission at the pump is neglected (σ_ep≈0), which is a common simplification.
# - Cross sections are approximated by a sum of Gaussians to capture the typical double-peak C-band shape.
# - You can adjust all parameters in the CONFIG section below.
#
# References (equations used here mirror standard EDFA textbooks/tutorials):
# - Gain coefficient: g(λ) = Γ_s (σ_e(λ) N2 − σ_a(λ) (N_t − N2));  G(λ) = exp[g(λ) L]
# - Spontaneous emission factor: n_sp(λ) = σ_e(λ) N2 / (σ_e(λ) N2 − σ_a(λ) N1)
# - ASE spectral density (per Hz, single polarization form used here): S_ASE(λ) = n_sp(λ) h ν (G(λ) − 1)
# - Noise Figure (linear): F(λ) = 2 n_sp(λ) (1 + 1/G(λ)); NF_dB = 10 log10 F
#
# -----------------------------------------------------------------------------

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from math import log, sqrt

# For nicely showing tables in the UI

# ---------------------------
# CONFIG (edit these values)
# ---------------------------

# Input signal (center wavelength and spectral width)
center_wl_nm = 1550.0   # nm
fwhm_nm      = 50.0      # nm
input_power_dBm = -10 # dBm (total signal power across the spectrum)

# Pump and EDFA settings
pump_wl_nm      = 980.0   # nm  (set to 1480.0 for 1480-nm pumping)
pump_power_mW   = 50.0    # mW  absorbed (effective) pump power (simplified)
L_m             = 20.0    # amplifier length in meters
Gamma_s         = 0.85    # signal confinement/overlap factor
Gamma_p         = 0.85    # pump confinement/overlap factor
Nt_m3           = 1.0e25  # total Erbium ion density (m^-3) ~1e25 is ~1e19 cm^-3
T1_s            = 10e-3   # upper-state lifetime (s) ~10 ms typical

# Mode/doped-area (effective area for flux; small-core EDF ~ 30–80 μm^2; we use 50 μm^2)
A_mode_m2 = 50e-12  # 50 μm^2

# Wavelength grid for simulation (C+L band window here for plots)
wl_min_nm = 1525.0
wl_max_nm = 1605.0
num_pts   = 801

# Cross-section model parameters (adjust to taste; values are *approximate* order of magnitude)
# Peaks chosen to mimic typical Er:SiO2 spectra near 1530–1560 nm
sigma_e_peaks = [
    # (amplitude [m^2], center [nm], FWHM [nm])
    (6.0e-25, 1531.0, 3.0),
    (3.0e-25, 1558.0, 6.0),
]
sigma_a_peaks = [
    (5.0e-25, 1530.0, 3.0),
    (1.0e-25, 1550.0, 10.0),
]

# Pump absorption cross-sections (very approximate order-of-magnitude values)
if abs(pump_wl_nm - 980.0) < 5.0:
    sigma_ap = 2.0e-24  # m^2 at 980 nm (absorption)
    sigma_ep = 0.0      # m^2 at 980 nm (emission negligible)
elif abs(pump_wl_nm - 1480.0) < 10.0:
    sigma_ap = 6.0e-25  # m^2 at 1480 nm (absorption, smaller than 980)
    sigma_ep = 2.0e-25  # m^2 at 1480 nm (emission non-negligible)
else:
    # Generic fallback
    sigma_ap = 5.0e-25
    sigma_ep = 0.0

# -----------------------------------
# Physical constants & helper funcs
# -----------------------------------

h = 6.62607015e-34   # Planck (J*s)
c = 2.99792458e8     # speed of light (m/s)

def fwhm_to_sigma(fwhm):
    """Convert FWHM to Gaussian sigma (same units)."""
    return fwhm / (2.0 * sqrt(2.0 * np.log(2.0)))

def gaussian(x, mu, fwhm, amp):
    """Gaussian with FWHM and amplitude."""
    sigma = fwhm_to_sigma(fwhm)
    return amp * np.exp(-0.5 * ((x - mu) / sigma) ** 2)

def sigma_spectrum_nm(wl_nm, peaks):
    """Sum of Gaussians to represent a cross-section spectrum over wavelength (nm)."""
    wl_nm = np.asarray(wl_nm)
    out = np.zeros_like(wl_nm, dtype=float)
    for amp, mu, fwhm in peaks:
        out += gaussian(wl_nm, mu, fwhm, amp)
    return out

def dBm_to_W(dBm):
    return 1e-3 * (10.0 ** (dBm / 10.0))

def W_to_dBm(W):
    return 10.0 * np.log10(np.maximum(W, 1e-18) / 1e-3)

# -----------------------------------
# Build wavelength grid & spectra
# -----------------------------------

wl_nm = np.linspace(wl_min_nm, wl_max_nm, num_pts)
wl_m  = wl_nm * 1e-9
nu_Hz = c / wl_m  # optical frequency

# Signal emission/absorption cross-sections vs wavelength
sigma_e = sigma_spectrum_nm(wl_nm, sigma_e_peaks)  # m^2
sigma_a = sigma_spectrum_nm(wl_nm, sigma_a_peaks)  # m^2

# ----------------------
# Population inversion
# ----------------------
# Pump photon flux Φ_p = P_pump / (A_mode * h * ν_p)
P_pump_W = pump_power_mW * 1e-3
nu_p     = c / (pump_wl_nm * 1e-9)
Phi_p    = Gamma_p * P_pump_W / (A_mode_m2 * h * nu_p)  # (photons / m^2 / s)

# Steady-state excited fraction (small-signal, neglect signal flux term):
# N2/Nt = (σ_ap Φ_p) / ( (σ_ap + σ_ep) Φ_p + 1/T1 )
N2_frac = (sigma_ap * Phi_p) / ((sigma_ap + sigma_ep) * Phi_p + 1.0 / T1_s)
N2 = N2_frac * Nt_m3
N1 = Nt_m3 - N2

# ----------------------
# Gain & Noise metrics
# ----------------------

# Small-signal gain coefficient g(λ)
g_per_m = Gamma_s * (sigma_e * N2 - sigma_a * N1)  # 1/m

# Total small-signal gain
G_linear = np.exp(g_per_m * L_m)
G_dB = 10.0 * np.log10(np.maximum(G_linear, 1e-12))

# Spontaneous emission factor n_sp(λ)
# n_sp = σ_e N2 / (σ_e N2 − σ_a N1) ; guard against division by zero
den = (sigma_e * N2 - sigma_a * N1)
den = np.where(np.abs(den) < 1e-50, 1e-50, den)
n_sp = (sigma_e * N2) / den

# Noise figure (linear & dB)
F_linear = 2.0 * n_sp * (1.0 + 1.0 / np.maximum(G_linear, 1e-12))
NF_dB = 10.0 * np.log10(F_linear)

# ASE spectral density per Hz (single-pol form per the provided formula)
S_ASE_W_per_Hz = n_sp * h * nu_Hz * (G_linear - 1.0)
S_ASE_W_per_Hz = np.maximum(S_ASE_W_per_Hz, 0.0)

# --------------------------------------------
# Input spectrum (Gaussian in wavelength axis)
# --------------------------------------------

Pin_W = dBm_to_W(input_power_dBm)

sig_sigma_nm = fwhm_to_sigma(fwhm_nm)
S_in_shape = np.exp(-0.5 * ((wl_nm - center_wl_nm) / sig_sigma_nm) ** 2)  # unnormalized
# Normalize so that ∫ S_in(λ) dλ = Pin_W
dlam = (wl_max_nm - wl_min_nm) / (num_pts - 1)
norm = np.trapz(S_in_shape, wl_nm)
S_in_W_per_nm = Pin_W * (S_in_shape / np.maximum(norm, 1e-30))

# Output signal spectrum (small-signal gain applied per wavelength)
S_out_W_per_nm = S_in_W_per_nm * G_linear

Pout_W = np.trapz(S_out_W_per_nm, wl_nm)
Pout_dBm = W_to_dBm(Pout_W)

# Estimate ASE power integrated over the signal spectral window (~±3σ of the input)
mask = np.abs(wl_nm - center_wl_nm) <= 3.0 * sig_sigma_nm
# Convert per-Hz density to per-nm via dν/dλ = -c/λ^2  -> |dν| = c/λ^2 dλ
dnu_per_nm = c / (wl_m**2) * 1e-9  # Hz per nm
S_ASE_W_per_nm = S_ASE_W_per_Hz * dnu_per_nm
P_ASE_W_window = np.trapz(S_ASE_W_per_nm[mask], wl_nm[mask])
P_ASE_dBm_window = W_to_dBm(P_ASE_W_window)

# ----------------------
# Build results table
# ----------------------

df = pd.DataFrame({
    "wavelength_nm": wl_nm,
    "gain_dB": G_dB,
    "NF_dB": NF_dB,
    "sigma_e_m2": sigma_e,
    "sigma_a_m2": sigma_a,
    "S_in_W_per_nm": S_in_W_per_nm,
    "S_out_W_per_nm": S_out_W_per_nm,
    "S_ASE_W_per_nm": S_ASE_W_per_nm
})

print(df.head(10))  # show first 10 rows


# ----------------------
# Plots
# ----------------------

# 1) Gain vs wavelength
plt.figure(figsize=(7.5, 4.5))
plt.plot(wl_nm, G_dB)
plt.xlabel("Wavelength (nm)")
plt.ylabel("Gain (dB)")
plt.title("EDFA Small-Signal Gain Spectrum")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# 2) Noise Figure vs wavelength
plt.figure(figsize=(7.5, 4.5))
plt.plot(wl_nm, NF_dB)
plt.xlabel("Wavelength (nm)")
plt.ylabel("Noise Figure (dB)")
plt.title("EDFA Noise Figure Spectrum")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# 3) Input vs Output spectra (power spectral density per nm)
plt.figure(figsize=(7.5, 4.5))
plt.plot(wl_nm, S_in_W_per_nm, label="Input PSD (W/nm)")
plt.plot(wl_nm, S_out_W_per_nm, label="Output PSD (W/nm)")
plt.xlabel("Wavelength (nm)")
plt.ylabel("Power Spectral Density (W/nm)")
plt.title("Input vs Output Spectra (Small-Signal)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# 4) ASE spectral density per nm
plt.figure(figsize=(7.5, 4.5))
plt.plot(wl_nm, S_ASE_W_per_nm)
plt.xlabel("Wavelength (nm)")
plt.ylabel("ASE Spectral Density (W/nm)")
plt.title("ASE Spectral Density (Single-Pol Model)")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# ----------------------
# Summary printout
# ----------------------
center_idx = np.argmin(np.abs(wl_nm - center_wl_nm))
summary = {
    "Center wavelength (nm)": center_wl_nm,
    "Input power (dBm)": input_power_dBm,
    "Pump wavelength (nm)": pump_wl_nm,
    "Pump power (mW)": pump_power_mW,
    "Fiber length (m)": L_m,
    "Er ion density Nt (m^-3)": Nt_m3,
    "Excited fraction N2/Nt": float(N2_frac),
    "Small-signal gain @ center (dB)": float(G_dB[center_idx]),
    "Noise figure @ center (dB)": float(NF_dB[center_idx]),
    "Total output power (dBm)": float(Pout_dBm),
    f"ASE power in ±3σ window around {center_wl_nm} nm (dBm)": float(P_ASE_dBm_window),
}

for k, v in summary.items():
    print(f"{k}: {v}")
