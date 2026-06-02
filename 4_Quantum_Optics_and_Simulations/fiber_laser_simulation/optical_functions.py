import numpy as np
from scipy import fft
from numba import jit, complex128, float64
import numba

def linear_operator_w(alpha, betaw, w):
    """Linear operator in frequency domain"""
    if np.isscalar(alpha):
        LOP = -alpha / 2 * np.ones_like(w)
    else:
        LOP = -alpha / 2
    
    if len(betaw) == len(w):
        LOP = LOP - 1j * betaw
        return np.fft.fftshift(LOP)
    else:
        for ii in range(len(betaw)):
            factorial_ii = 1
            for j in range(1, ii + 1):
                factorial_ii *= j
            LOP = LOP - 1j * betaw[ii] * (w)**ii / factorial_ii
    
    return LOP

@jit(nopython=True)
def coupler(u1i, u2i, rho):
    """Simulate output coupler"""
    if rho > 1:
        rho = 1
    elif rho < 0:
        rho = 0
    
    u1o = np.sqrt(1 - rho) * u1i  # Transmitted (stays in cavity)
    u2o = np.sqrt(rho) * u1i      # Coupled out
    
    return u1o, u2o

@jit(nopython=True)
def saturable_absorber(u, modulation_depth, saturation_power):
    """Saturable absorber with monotonic transfer function (T1 from paper)"""
    P_t = np.abs(u)**2  # Instantaneous power
    
    # T1 = 1 - m/(1 + P(t)/P_sat) from paper
    transmission = 1 - modulation_depth / (1 + P_t / saturation_power)
    
    return u * np.sqrt(transmission)

def yb_gain_saturated(u, dt, g, E_sat, gain_bw, lambda_c):
    """Ytterbium gain saturation model from paper"""
    # Calculate pulse energy
    E_pulse = np.sum(np.abs(u)**2) * dt
    
    # Saturated gain: G = g / (1 + E_pulse/E_sat)
    gain_coeff = g / (1 + E_pulse / E_sat)
    
    return gain_coeff

def parabolic_gain_spectrum(f, fc, gain_bw):
    """Parabolic gain spectrum for Ytterbium (40 nm bandwidth)"""
    f_norm = (f - fc) / (gain_bw / 2)
    
    # Parabolic profile
    gain_spectrum = np.maximum(1 - f_norm**2, 0.1)
    
    return gain_spectrum

def filter_gaussian(ui, f3dB, fc, fo, df):
    """Gaussian spectral filter from paper"""
    Ui = fft.fft(ui)
    N = len(Ui)
    
    f_vec = np.fft.fftshift(np.linspace(-(N/2)*df, (N/2-1)*df, N) + fo)
    
    # Gaussian filter: F(ω) = exp[-(ω/δω)²]
    # δω = 2πc(δλ/1.66λ²) from paper
    delta_omega = 2 * np.pi * 299792.458 * (f3dB / (1.66 * 1030**2))
    
    Tf = np.exp(-((f_vec - fc) / delta_omega)**2)
    
    return fft.ifft(Ui * Tf)

def raman_response_w(t, raman_flag=0):
    """Raman response - disabled initially for stability"""
    return np.zeros_like(t, dtype=complex), 0.0

def nonlinear_operator_w(u_t, gamma, w, fo, fr, hrw, dt, ssp=0):
    """Nonlinear operator for Ginzburg-Landau equation"""
    if gamma == 0:
        return np.zeros_like(u_t, dtype=complex)
    
    # Simple Kerr nonlinearity: iγ|A|²A
    intensity = u_t * np.conj(u_t)
    NLOP = 1j * gamma * np.fft.fft(u_t * intensity)
    
    return NLOP

def white_gaussian_noise(nt, noise_power=1e-6):
    """Generate white Gaussian noise as initial seed"""
    np.random.seed(42)  # For reproducibility
    
    # Complex white Gaussian noise
    noise_real = np.random.normal(0, np.sqrt(noise_power/2), nt)
    noise_imag = np.random.normal(0, np.sqrt(noise_power/2), nt)
    
    return noise_real + 1j * noise_imag

def fwhm(x):
    """Calculate Full Width at Half Maximum"""
    if len(x) == 0 or np.max(x) == 0:
        return 0, 0, 0
        
    nsize = len(x)
    peak = np.max(x)
    ind_peak = np.argmax(x)
    half_peak = peak / 2
    
    x_l = x[:ind_peak]
    x_r = x[ind_peak+1:]
    
    # Find half maximum points
    I_l_candidates = np.where(x_l[::-1] <= half_peak)[0]
    I_r_candidates = np.where(x_r <= half_peak)[0]
    
    if len(I_l_candidates) == 0:
        width = nsize
        I_l = 0
        I_r = nsize - 1
    elif len(I_r_candidates) == 0:
        width = nsize
        I_l = 0
        I_r = nsize - 1
    else:
        I_l = I_l_candidates[0]
        I_r = I_r_candidates[0]
        width = I_l + I_r
        I_l = ind_peak - I_l
        I_r = ind_peak + I_r
    
    return width, I_l, I_r

def calculate_spectral_width(spectrum, wavelengths, level_db):
    """Calculate spectral width at given dB level"""
    spectrum_db = 10 * np.log10(np.maximum(spectrum, np.max(spectrum) * 1e-10))
    threshold = np.max(spectrum_db) - level_db
    
    indices = np.where(spectrum_db >= threshold)[0]
    if len(indices) > 0:
        width = wavelengths[indices[-1]] - wavelengths[indices[0]]
    else:
        width = 0
    
    return width

def xcorr_normal(x, y, lag):
    """Normalized cross-correlation"""
    nt = len(x)
    if lag >= len(x):
        lag = len(x) - 1
    
    out = np.correlate(x, y, mode='full')
    
    norm_factor = np.sqrt(np.sum(x**2) * np.sum(y**2))
    if norm_factor > 0:
        out = out / norm_factor
    
    return out

# Legacy functions for compatibility
@jit(nopython=True)
def laser_sa(u, Isa):
    """Legacy saturable absorber function"""
    return saturable_absorber(u, 0.6, Isa)

def gain_saturated2(Pin, gssdB, PsatdBm):
    """Legacy EDFA gain function - not used in ANDi laser"""
    gss = 10**(gssdB/10)
    Psat = (10**(PsatdBm/10)) / 1000
    
    if Pin <= 0:
        return gss
    
    gain = gss / (1 + Pin / Psat)
    return max(min(gain, gss), 0.1)

def edfa_gain_spectrum(f, fc, fbw):
    """Legacy EDFA gain spectrum - not used in ANDi laser"""
    f_norm = (f - fc) / (fbw / 2)
    gain_spectrum = np.exp(-0.5 * f_norm**2)
    gain_spectrum = np.maximum(gain_spectrum, 0.5)
    return gain_spectrum
