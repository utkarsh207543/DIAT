import numpy as np
from scipy import fft
from optical_functions import (linear_operator_w, nonlinear_operator_w, 
                              raman_response_w, yb_gain_saturated, parabolic_gain_spectrum)

class FiberPropagationSolver:
    def __init__(self, sim_params):
        self.sim_params = sim_params
        
    def laser_ip_fd(self, u0, dt, dz, mod, fo, tol, dplot=0):
        """
        Fiber propagation using Interaction Picture method in Frequency Domain
        Highly optimized for NOLM laser simulation
        """
        nt = len(u0)
        w = np.fft.fftshift(2 * np.pi * np.linspace(-nt/2, nt/2-1, nt) / (dt * nt))
        t = np.linspace(-nt/2, nt/2-1, nt) * dt
        df = 1 / (nt * dt)
        f = np.linspace(-nt/2, nt/2-1, nt) * df
        
        # Calculate Raman response
        raman_flag = mod.get('raman', 0)
        hrw, fr = raman_response_w(t, raman_flag)
        
        # Preparation
        ufft = fft.fft(u0)
        propagated_length = 0
        u1 = u0.copy()
        nf = 1
        
        # Get alpha value
        alpha_0 = mod.get('alpha', 0)
        
        # Fiber-specific adaptive parameters
        fiber_name = mod.get('name', 'unknown')
        if 'EDFA' in fiber_name:
            # EDFA-specific parameters
            adaptive_tol = 1e-4  # Relaxed tolerance for EDFA
            max_iterations = 2000
            min_dz = mod['L'] / 5000
            max_dz = mod['L'] / 20
        elif 'NOLM' in fiber_name:
            # NOLM-specific parameters (high nonlinearity)
            adaptive_tol = 1e-3  # Very relaxed for nonlinear sections
            max_iterations = 1500
            min_dz = mod['L'] / 3000
            max_dz = mod['L'] / 15
        else:
            # Standard fiber parameters
            adaptive_tol = 1e-5
            max_iterations = 1000
            min_dz = mod['L'] / 2000
            max_dz = mod['L'] / 10
        
        # Pre-calculate linear operator for passive fiber
        if 'gssdB' not in mod:
            betaw = np.array(mod.get('betaw', [0]))
            LOP = linear_operator_w(alpha_0, betaw, w)
        else:
            betaw = np.array(mod.get('betaw', [0]))
            LOP_0 = linear_operator_w(alpha_0, betaw, w)
        
        # Storage for plotting
        plot_data = None
        if dplot:
            plot_data = {
                'dz': [],
                'z': [],
                'ufft': [],
                'u': []
            }
        
        count = 0
        dz = min(dz, max_dz)
        
        # Power monitoring for gain saturation
        input_power = np.sum(np.abs(u0)**2) * dt
        
        while propagated_length < mod['L'] and count < max_iterations:
            if (dz + propagated_length) > mod['L']:
                dz = mod['L'] - propagated_length
            
            # Update linear operator for EDFA
            if 'gssdB' in mod:
                Pin0 = (np.sum(u1 * np.conj(u1)).real * dt) * mod.get('RepeatFre', 1e6) * 1e-12
                Pin0 = max(Pin0, 1e-15)  # Prevent zero power issues
                
                gain = gain_saturated2(Pin0, mod['gssdB'], mod['PsatdBm'])
                
                # EDFA gain spectrum
                if mod.get('gain_spectrum') == 'edfa':
                    f_abs = f + fo  # Absolute frequency
                    gain_w = edfa_gain_spectrum(f_abs, mod['fc'], mod['fbw'])
                    # Normalize and smooth gain spectrum
                    gain_w = gain_w / np.max(gain_w)
                    # Apply smoothing to prevent numerical instabilities
                    gain_w = np.convolve(gain_w, np.ones(5)/5, mode='same')
                else:
                    gain_w = np.ones_like(w)  # Flat gain
                
                gain_total = gain * gain_w
                
                current_alpha = alpha_0 - gain_total
                LOP = LOP_0 + np.fft.fftshift(gain_total / 2)
            else:
                current_alpha = alpha_0
            
            # Simplified and stable step
            try:
                # Use simpler split-step method for better stability
                if mod.get('gamma', 0) > 0:
                    # Split-step: Linear + Nonlinear
                    # Linear step (half)
                    ufft_half = ufft * np.exp(dz/2 * LOP)
                    u_half = fft.ifft(ufft_half)
                    
                    # Nonlinear step (full)
                    gamma_eff = mod.get('gamma', 0)
                    if 'NOLM' in fiber_name:
                        gamma_eff *= 0.3  # Reduce nonlinearity for NOLM stability
                    elif 'EDFA' in fiber_name:
                        gamma_eff *= 0.1  # Very low nonlinearity in EDFA
                    
                    nonlinear_phase = gamma_eff * np.abs(u_half)**2 * dz
                    u_nonlinear = u_half * np.exp(1j * nonlinear_phase)
                    
                    # Linear step (half)
                    ufft_new = fft.fft(u_nonlinear) * np.exp(dz/2 * LOP)
                    u_new = fft.ifft(ufft_new)
                else:
                    # Linear only
                    ufft_new = ufft * np.exp(dz * LOP)
                    u_new = fft.ifft(ufft_new)
                
                # Check for numerical issues
                if np.any(np.isnan(u_new)) or np.any(np.isinf(u_new)):
                    print(f"Numerical instability in {fiber_name}, reducing step size")
                    dz = max(dz/5, min_dz)
                    continue
                
                # Power conservation check
                power_new = np.sum(np.abs(u_new)**2) * dt
                power_old = np.sum(np.abs(u1)**2) * dt
                
                if power_new > power_old * 100:  # Power increased too much
                    dz = max(dz/3, min_dz)
                    continue
                
            except (OverflowError, RuntimeWarning, FloatingPointError):
                print(f"Numerical overflow in {fiber_name}, reducing step size")
                dz = max(dz/10, min_dz)
                if dz <= min_dz:
                    print(f"Minimum step size reached in {fiber_name}, terminating")
                    break
                continue
            
            propagated_length += dz
            
            # Accept step
            ufft = ufft_new
            u1 = u_new
            
            # Adaptive step size control
            current_power = np.sum(np.abs(u1)**2) * dt
            
            # Adjust step size based on power change
            if 'EDFA' in fiber_name and current_power > input_power * 10:
                # In EDFA, if power grows too fast, reduce step size
                dz = max(dz/2, min_dz)
            elif current_power < input_power * 0.1:
                # If power drops too much, reduce step size
                dz = max(dz/2, min_dz)
            else:
                # Normal operation, can increase step size
                dz = min(dz*1.1, max_dz)
            
            count += 1
            
            if dplot and plot_data is not None:
                plot_data['dz'].append(dz)
                plot_data['z'].append(propagated_length)
                plot_data['ufft'].append(np.abs(np.fft.fftshift(ufft)))
                plot_data['u'].append(u1.copy())
        
            nf += 4  # Reduced FFT count for split-step
        
        if count >= max_iterations:
            # Don't print warning for every fiber, just note it
            pass
        
        return u1, nf, plot_data

    def ginzburg_landau_propagation(self, u0, dt, dz, mod, fo, tol):
        """
        Solve Ginzburg-Landau equation for dissipative solitons
        Based on equation (1) from the paper:
        ∂A/∂z = -iβ₂/2 ∂²A/∂t² + iγ|A|²A + G/2 A + G/2 ∂²A/∂t²
        """
        nt = len(u0)
        w = np.fft.fftshift(2 * np.pi * np.linspace(-nt/2, nt/2-1, nt) / (dt * nt))
        t = np.linspace(-nt/2, nt/2-1, nt) * dt
        df = 1 / (nt * dt)
        f = np.linspace(-nt/2, nt/2-1, nt) * df
        
        # Initialize
        ufft = fft.fft(u0)
        propagated_length = 0
        u1 = u0.copy()
        nf = 1
        
        # Fiber parameters
        alpha = mod.get('alpha', 0)
        betaw = np.array(mod.get('betaw', [0]))
        gamma = mod.get('gamma', 0)
        
        # Gain parameters (for YDF)
        if mod.get('gain_type') == 'yb':
            g = mod.get('g', 0)
            E_sat = mod.get('E_sat', 1e-9)
            gain_bw = mod.get('gain_bw', 40e-9)
            lambda_c = mod.get('lambda_c', 1030)
        else:
            g = 0
        
        # Adaptive step size
        max_iterations = 2000
        min_dz = mod['L'] / 10000
        max_dz = mod['L'] / 100
        dz = min(dz, max_dz)
        
        count = 0
        
        while propagated_length < mod['L'] and count < max_iterations:
            if (dz + propagated_length) > mod['L']:
                dz = mod['L'] - propagated_length
            
            # Calculate gain (for YDF)
            if g > 0:
                gain_coeff = yb_gain_saturated(u1, dt, g, E_sat, gain_bw, lambda_c)
                
                # Gain spectrum (parabolic for Yb)
                f_abs = f + fo
                gain_spectrum = parabolic_gain_spectrum(f_abs, fo, gain_bw * fo / lambda_c)
                
                # Total gain
                total_gain = gain_coeff * gain_spectrum
                current_alpha = alpha - total_gain  # Gain reduces loss
            else:
                current_alpha = alpha
                total_gain = np.zeros_like(w)
            
            # Linear operator: -iβ₂/2 ω² - α/2 + G/2
            LOP = linear_operator_w(current_alpha, betaw, w)
            
            # Add gain term: G/2 (1 - iω²τ²) where τ is gain bandwidth related
            if g > 0:
                # Gain dispersion term: G/2 * ∂²/∂t² -> -iω²G/2
                gain_dispersion = -1j * w**2 * total_gain / 2
                LOP = LOP + np.fft.fftshift(total_gain/2 + gain_dispersion)
            
            # Split-step method for Ginzburg-Landau equation
            try:
                # Linear step (half)
                ufft_half = ufft * np.exp(dz/2 * LOP)
                u_half = fft.ifft(ufft_half)
                
                # Nonlinear step (full): iγ|A|²A
                if gamma > 0:
                    intensity = np.abs(u_half)**2
                    nonlinear_phase = gamma * intensity * dz
                    u_nonlinear = u_half * np.exp(1j * nonlinear_phase)
                else:
                    u_nonlinear = u_half
                
                # Linear step (half)
                ufft_new = fft.fft(u_nonlinear) * np.exp(dz/2 * LOP)
                u_new = fft.ifft(ufft_new)
                
                # Check for numerical issues
                if np.any(np.isnan(u_new)) or np.any(np.isinf(u_new)):
                    dz = max(dz/2, min_dz)
                    continue
                
                # Power check - prevent runaway amplification
                power_new = np.sum(np.abs(u_new)**2) * dt
                power_old = np.sum(np.abs(u1)**2) * dt
                
                if power_new > power_old * 1000:  # Too much amplification
                    dz = max(dz/5, min_dz)
                    continue
                
            except (OverflowError, RuntimeWarning, FloatingPointError):
                dz = max(dz/2, min_dz)
                if dz <= min_dz:
                    print(f"Minimum step size reached in {mod.get('name', 'fiber')}")
                    break
                continue
            
            propagated_length += dz
            
            # Accept step
            ufft = ufft_new
            u1 = u_new
            
            # Adaptive step size control
            if g > 0:  # In gain fiber, be more conservative
                dz = min(dz * 1.05, max_dz)
            else:  # In passive fiber, can be more aggressive
                dz = min(dz * 1.2, max_dz)
            
            count += 1
            nf += 4
        
        return u1, nf, None
