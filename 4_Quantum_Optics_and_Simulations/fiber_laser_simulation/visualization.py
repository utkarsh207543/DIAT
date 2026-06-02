import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib.animation as animation
from scipy import fft

class LaserVisualization:
    def __init__(self, sim_params, components):
        self.sim_params = sim_params
        self.components = components
        self.fig = None
        self.axes = None
        self.lines = {}
        self.images = {}
        
    def setup_dashboard(self):
        """Setup the main dashboard with all plots"""
        plt.ion()  # Turn on interactive mode
        
        # Close any existing figures
        plt.close('all')
        
        # Create main figure with subplots
        self.fig = plt.figure(figsize=(16, 12))
        self.fig.suptitle('Fiber Laser Simulation Dashboard', fontsize=16, fontweight='bold')
        
        # Create grid layout
        gs = GridSpec(3, 4, figure=self.fig, hspace=0.3, wspace=0.3)
        
        # Current pulse shape
        self.axes = {}
        self.axes['pulse'] = self.fig.add_subplot(gs[0, 0])
        self.axes['pulse'].set_title('Current Pulse Shape')
        self.axes['pulse'].set_xlabel('Time (ps)')
        self.axes['pulse'].set_ylabel('Power (W)')
        self.axes['pulse'].grid(True)
        
        # Current spectrum
        self.axes['spectrum'] = self.fig.add_subplot(gs[0, 1])
        self.axes['spectrum'].set_title('Current Spectrum')
        self.axes['spectrum'].set_xlabel('Wavelength (nm)')
        self.axes['spectrum'].set_ylabel('Normalized Intensity')
        self.axes['spectrum'].grid(True)
        
        # Power evolution
        self.axes['power_evo'] = self.fig.add_subplot(gs[0, 2])
        self.axes['power_evo'].set_title('Power Evolution')
        self.axes['power_evo'].set_xlabel('Round Trip')
        self.axes['power_evo'].set_ylabel('Peak Power (W)')
        self.axes['power_evo'].grid(True)
        self.axes['power_evo'].set_yscale('log')
        
        # Energy evolution
        self.axes['energy_evo'] = self.fig.add_subplot(gs[0, 3])
        self.axes['energy_evo'].set_title('Energy Evolution')
        self.axes['energy_evo'].set_xlabel('Round Trip')
        self.axes['energy_evo'].set_ylabel('Pulse Energy (pJ)')
        self.axes['energy_evo'].grid(True)
        self.axes['energy_evo'].set_yscale('log')
        
        # Pulse evolution (2D)
        self.axes['pulse_2d'] = self.fig.add_subplot(gs[1, :2])
        self.axes['pulse_2d'].set_title('Pulse Evolution Over Round Trips')
        self.axes['pulse_2d'].set_xlabel('Time (ps)')
        self.axes['pulse_2d'].set_ylabel('Round Trip')
        
        # Spectrum evolution (2D)
        self.axes['spectrum_2d'] = self.fig.add_subplot(gs[1, 2:])
        self.axes['spectrum_2d'].set_title('Spectrum Evolution Over Round Trips')
        self.axes['spectrum_2d'].set_xlabel('Wavelength (nm)')
        self.axes['spectrum_2d'].set_ylabel('Round Trip')
        
        # Statistics text
        self.axes['stats'] = self.fig.add_subplot(gs[2, :2])
        self.axes['stats'].axis('off')
        self.axes['stats'].set_title('Current Statistics', loc='left', fontweight='bold')
        
        # Autocorrelation
        self.axes['autocorr'] = self.fig.add_subplot(gs[2, 2])
        self.axes['autocorr'].set_title('Autocorrelation')
        self.axes['autocorr'].set_xlabel('Delay (ps)')
        self.axes['autocorr'].set_ylabel('Intensity')
        self.axes['autocorr'].grid(True)
        
        # Phase
        self.axes['phase'] = self.fig.add_subplot(gs[2, 3])
        self.axes['phase'].set_title('Pulse Phase')
        self.axes['phase'].set_xlabel('Time (ps)')
        self.axes['phase'].set_ylabel('Phase (rad)')
        self.axes['phase'].grid(True)
        
        # Initialize empty lines
        self.lines['pulse'], = self.axes['pulse'].plot([], [], 'b-', linewidth=2)
        self.lines['spectrum'], = self.axes['spectrum'].plot([], [], 'r-', linewidth=2)
        self.lines['power_evo'], = self.axes['power_evo'].plot([], [], 'g-', marker='o', markersize=4)
        self.lines['energy_evo'], = self.axes['energy_evo'].plot([], [], 'm-', marker='s', markersize=4)
        self.lines['autocorr'], = self.axes['autocorr'].plot([], [], 'c-', linewidth=2)
        self.lines['phase'], = self.axes['phase'].plot([], [], 'k-', linewidth=2)
        
        plt.tight_layout()
        plt.show(block=False)
        
    def update_dashboard(self, iteration, uout, power_evolution, energy_evolution, u_z, spec_z):
        """Update all plots in the dashboard"""
        try:
            # Calculate current parameters
            Eout = np.abs(uout)**2
            current_power = np.max(Eout)
            current_energy = self.sim_params.dt * np.sum(Eout)
            
            # Current pulse shape
            self.lines['pulse'].set_data(self.sim_params.t, Eout)
            self.axes['pulse'].relim()
            self.axes['pulse'].autoscale_view()
            
            # Current spectrum
            spec = np.fft.fftshift(fft.fft(uout))
            specnorm = np.abs(spec)**2
            if np.max(specnorm) > 0:
                specnorm = specnorm / np.max(specnorm)
            lambda_vec = self.sim_params.c / (self.sim_params.f + self.sim_params.fo)
            self.lines['spectrum'].set_data(lambda_vec, specnorm)
            self.axes['spectrum'].relim()
            self.axes['spectrum'].autoscale_view()
            
            # Power evolution
            iterations = range(1, len(power_evolution) + 1)
            self.lines['power_evo'].set_data(iterations, power_evolution)
            self.axes['power_evo'].relim()
            self.axes['power_evo'].autoscale_view()
            
            # Energy evolution
            self.lines['energy_evo'].set_data(iterations, energy_evolution)
            self.axes['energy_evo'].relim()
            self.axes['energy_evo'].autoscale_view()
            
            # 2D pulse evolution
            if iteration > 0:
                extent = [self.sim_params.t[0], self.sim_params.t[-1], 1, iteration+1]
                pulse_data = np.abs(u_z[:iteration+1, :])**2
                
                if hasattr(self, 'pulse_im'):
                    self.pulse_im.remove()
                self.pulse_im = self.axes['pulse_2d'].imshow(pulse_data, 
                                                           aspect='auto', extent=extent, 
                                                           origin='lower', cmap='hot')
                
                # 2D spectrum evolution
                extent_spec = [lambda_vec[0], lambda_vec[-1], 1, iteration+1]
                spec_data = spec_z[:iteration+1, :].real
                
                if hasattr(self, 'spec_im'):
                    self.spec_im.remove()
                self.spec_im = self.axes['spectrum_2d'].imshow(spec_data, 
                                                             aspect='auto', extent=extent_spec, 
                                                             origin='lower', cmap='hot')
            
            # Autocorrelation
            AC = np.correlate(Eout, Eout, mode='full')
            AC = AC / np.max(AC) if np.max(AC) > 0 else AC
            time_delay = np.linspace(-self.sim_params.time + self.sim_params.dt, 
                                   self.sim_params.time - self.sim_params.dt, len(AC))
            self.lines['autocorr'].set_data(time_delay, AC)
            self.axes['autocorr'].relim()
            self.axes['autocorr'].autoscale_view()
            
            # Phase
            phase = np.angle(uout)
            self.lines['phase'].set_data(self.sim_params.t, phase)
            self.axes['phase'].relim()
            self.axes['phase'].autoscale_view()
            
            # Update statistics text
            from optical_functions import fwhm
            width, _, _ = fwhm(Eout)
            pulse_width = width * self.sim_params.dt
            
            # Calculate spectral bandwidth
            spec_width, _, _ = fwhm(specnorm)
            lambda_bandwidth = spec_width * abs(lambda_vec[1] - lambda_vec[0]) if spec_width > 0 else 0
            
            # Calculate central wavelength
            lambda_center = lambda_vec[np.argmax(specnorm)]
            
            stats_text = f"""
Round Trip: {iteration + 1}
Peak Power: {current_power:.3e} W
Pulse Energy: {current_energy:.3e} pJ
Pulse Width (FWHM): {pulse_width:.2f} ps
Central Wavelength: {lambda_center:.2f} nm
Spectral Bandwidth: {lambda_bandwidth:.2f} nm
Repetition Rate: {self.components.RepeatFre/1e6:.2f} MHz
Average Power: {current_energy * self.components.RepeatFre * 1e-12:.6f} mW

Cavity Length: {self.components.Length_cavity*1000:.2f} m
Time-Bandwidth Product: {pulse_width * lambda_bandwidth / lambda_center**2 * self.sim_params.c:.3f}
            """
            
            self.axes['stats'].clear()
            self.axes['stats'].text(0.05, 0.95, stats_text, transform=self.axes['stats'].transAxes,
                                  fontsize=10, verticalalignment='top', fontfamily='monospace')
            self.axes['stats'].axis('off')
            
            # Update the display
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
            plt.pause(0.01)
            
        except Exception as e:
            print(f"Warning: Dashboard update failed: {e}")
    
    def show_final_summary(self, final_iteration, uout, power_evolution, energy_evolution):
        """Show final summary in a separate window"""
        try:
            # Create summary figure
            summary_fig, summary_axes = plt.subplots(2, 2, figsize=(12, 8))
            summary_fig.suptitle('Final Simulation Summary', fontsize=14, fontweight='bold')
            
            # Final pulse
            Eout = np.abs(uout)**2
            summary_axes[0, 0].plot(self.sim_params.t, Eout, 'b-', linewidth=2)
            summary_axes[0, 0].set_title('Final Pulse Shape')
            summary_axes[0, 0].set_xlabel('Time (ps)')
            summary_axes[0, 0].set_ylabel('Power (W)')
            summary_axes[0, 0].grid(True)
            
            # Final spectrum
            spec = np.fft.fftshift(fft.fft(uout))
            specnorm = np.abs(spec)**2
            if np.max(specnorm) > 0:
                specnorm = specnorm / np.max(specnorm)
            lambda_vec = self.sim_params.c / (self.sim_params.f + self.sim_params.fo)
            summary_axes[0, 1].plot(lambda_vec, specnorm, 'r-', linewidth=2)
            summary_axes[0, 1].set_title('Final Spectrum')
            summary_axes[0, 1].set_xlabel('Wavelength (nm)')
            summary_axes[0, 1].set_ylabel('Normalized Intensity')
            summary_axes[0, 1].grid(True)
            
            # Power evolution
            iterations = range(1, len(power_evolution) + 1)
            summary_axes[1, 0].semilogy(iterations, power_evolution, 'g-', marker='o', markersize=4)
            summary_axes[1, 0].set_title('Power Evolution')
            summary_axes[1, 0].set_xlabel('Round Trip')
            summary_axes[1, 0].set_ylabel('Peak Power (W)')
            summary_axes[1, 0].grid(True)
            
            # Energy evolution
            summary_axes[1, 1].semilogy(iterations, energy_evolution, 'm-', marker='s', markersize=4)
            summary_axes[1, 1].set_title('Energy Evolution')
            summary_axes[1, 1].set_xlabel('Round Trip')
            summary_axes[1, 1].set_ylabel('Pulse Energy (pJ)')
            summary_axes[1, 1].grid(True)
            
            plt.tight_layout()
            plt.show()
            
            # Print comprehensive summary
            from optical_functions import fwhm
            width, _, _ = fwhm(Eout)
            pulse_width = width * self.sim_params.dt
            current_energy = self.sim_params.dt * np.sum(Eout)
            
            spec_width, _, _ = fwhm(specnorm)
            lambda_bandwidth = spec_width * abs(lambda_vec[1] - lambda_vec[0]) if spec_width > 0 else 0
            lambda_center = lambda_vec[np.argmax(specnorm)]
            
            print("\n" + "="*60)
            print("FINAL SIMULATION RESULTS")
            print("="*60)
            print(f"Simulation completed after {final_iteration + 1} round trips")
            print(f"Design type: Saturable Absorber (SA)")
            print("\nPulse Characteristics:")
            print(f"  Peak Power:           {np.max(Eout):.3e} W")
            print(f"  Pulse Energy:         {current_energy:.3e} pJ")
            print(f"  Pulse Width (FWHM):   {pulse_width:.2f} ps")
            print(f"  Central Wavelength:   {lambda_center:.2f} nm")
            print(f"  Spectral Bandwidth:   {lambda_bandwidth:.2f} nm")
            print(f"  Time-Bandwidth Prod:  {pulse_width * lambda_bandwidth / lambda_center**2 * self.sim_params.c:.3f}")
            print("\nLaser Parameters:")
            print(f"  Repetition Rate:      {self.components.RepeatFre/1e6:.2f} MHz")
            print(f"  Average Power:        {current_energy * self.components.RepeatFre * 1e-12:.6f} mW")
            print(f"  Cavity Length:        {self.components.Length_cavity*1000:.2f} m")
            print("\nEvolution Statistics:")
            print(f"  Initial Power:        {power_evolution[0]:.3e} W")
            print(f"  Final Power:          {power_evolution[-1]:.3e} W")
            print(f"  Power Growth Factor:  {power_evolution[-1]/power_evolution[0]:.2f}")
            print("="*60)
            
        except Exception as e:
            print(f"Error creating summary: {e}")

    def close_all(self):
        """Close all figures"""
        plt.close('all')
