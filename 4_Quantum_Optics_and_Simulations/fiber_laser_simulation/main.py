import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from scipy import fft
import time

from sim_parameters import SimulationParameters
from components import FiberComponents
from laser_designs import LaserDesigns
from optical_functions import white_gaussian_noise, fwhm, calculate_spectral_width
from visualization import LaserVisualization

class ANDiFiberLaserSimulation:
    def __init__(self):
        print("Initializing All-Normal Dispersion Yb Fiber Laser Simulation...")
        self.sim_params = SimulationParameters()
        self.components = FiberComponents(self.sim_params)
        self.laser_designs = LaserDesigns(self.components, self.sim_params)
        
        # Initialize storage arrays
        self.spec_z = np.zeros((self.sim_params.N_trip, self.sim_params.nt), dtype=complex)
        self.u_z = np.zeros((self.sim_params.N_trip, self.sim_params.nt), dtype=complex)
        
        # Initialize visualization
        self.viz = LaserVisualization(self.sim_params, self.components)
        
        print("Initialization complete!")
    
    def run_simulation(self, filter_bandwidth=20, enable_dashboard=True, update_frequency=50):
        """Run ANDi laser simulation with specified filter bandwidth"""
        print(f"Starting ANDi laser simulation with {filter_bandwidth} nm filter...")
        
        # Update filter bandwidth
        self.components.filter['lambda_bw'] = filter_bandwidth
        self.components.filter['f3dB'] = (self.sim_params.c / (self.sim_params.lx)**2 * 
                                         filter_bandwidth)
        
        # Setup dashboard if enabled
        if enable_dashboard:
            self.viz.setup_dashboard()
        
        # Initialize with white Gaussian noise (as in paper)
        u0 = white_gaussian_noise(self.sim_params.nt, noise_power=1e-6)
        u = u0.copy()
        
        start_time = time.time()
        
        # Store evolution data
        power_evolution = []
        energy_evolution = []
        pulse_width_evolution = []
        spectral_width_3db = []
        spectral_width_20db = []
        
        # Track dissipative soliton formation
        stable_count = 0
        explosion_events = 0
        
        for ii in range(self.sim_params.N_trip):
            # Calculate metrics
            power = np.max(np.abs(u)**2).real
            energy = self.sim_params.dt * np.sum(np.abs(u)**2).real
            
            # Pulse width
            intensity = np.abs(u)**2
            width, _, _ = fwhm(intensity)
            pulse_width = width * self.sim_params.dt
            
            # Spectral analysis
            spec = np.fft.fftshift(fft.fft(u))
            specnorm = np.abs(spec)**2
            if np.max(specnorm) > 0:
                specnorm = specnorm / np.max(specnorm)
            
            # Calculate spectral widths at 3dB and 20dB levels
            lambda_vec = self.sim_params.c / (self.sim_params.f + self.sim_params.fo)
            width_3db = calculate_spectral_width(specnorm, lambda_vec, 3)
            width_20db = calculate_spectral_width(specnorm, lambda_vec, 20)
            
            # Store data
            power_evolution.append(power)
            energy_evolution.append(energy)
            pulse_width_evolution.append(pulse_width)
            spectral_width_3db.append(width_3db)
            spectral_width_20db.append(width_20db)
            
            # Progress reporting
            if ii < 100 or ii % 100 == 0:
                print(f'Round Trip {ii+1:4d}: Power = {power:.2e} W, '
                      f'Energy = {energy:.2e} pJ, Width = {pulse_width:.2f} ps, '
                      f'Spec 3dB = {width_3db:.1f} nm')
            
            # Detect soliton explosions (sudden power changes)
            if ii > 10:
                power_ratio = power / power_evolution[ii-1] if power_evolution[ii-1] > 0 else 1
                if power_ratio > 5 or power_ratio < 0.2:
                    explosion_events += 1
                    if explosion_events < 5:  # Print first few explosions
                        print(f"*** Soliton explosion detected at round trip {ii+1} ***")
            
            # Apply laser design
            try:
                u, uout = self.laser_designs.design_andi_laser(u, 0)
            except Exception as e:
                print(f"Error in round trip {ii+1}: {e}")
                break
            
            # Store results
            spec_out = np.fft.fftshift(fft.fft(uout))
            specnorm_out = np.abs(spec_out)**2
            if np.max(specnorm_out) > 0:
                specnorm_out = specnorm_out / np.max(specnorm_out)
            
            self.spec_z[ii, :] = specnorm_out
            self.u_z[ii, :] = uout
            
            # Update dashboard
            if enable_dashboard and ii % update_frequency == 0:
                self.viz.update_dashboard(ii, uout, power_evolution, energy_evolution, 
                                        self.u_z, self.spec_z)
            
            # Check for stability (last 100 round trips)
            if ii > self.sim_params.N_trip - 100:
                recent_powers = power_evolution[-50:] if len(power_evolution) >= 50 else power_evolution
                if len(recent_powers) >= 10:
                    power_variation = np.std(recent_powers) / np.mean(recent_powers)
                    if power_variation < 0.05:
                        stable_count += 1
            
            # Stop if power becomes too low
            if power < 1e-15:
                print("Power too low - laser died")
                break
        
        end_time = time.time()
        
        # Analyze final state
        final_power = power_evolution[-1] if power_evolution else 0
        final_energy = energy_evolution[-1] if energy_evolution else 0
        final_width = pulse_width_evolution[-1] if pulse_width_evolution else 0
        
        print(f"\nSimulation completed in {end_time - start_time:.2f} seconds")
        print(f"Filter bandwidth: {filter_bandwidth} nm")
        print(f"Final power: {final_power:.2e} W")
        print(f"Final energy: {final_energy:.2e} pJ")
        print(f"Final pulse width: {final_width:.2f} ps")
        print(f"Explosion events detected: {explosion_events}")
        
        # Determine operation state
        if stable_count > 80:
            print("*** Stable dissipative soliton achieved ***")
        elif explosion_events > 50:
            print("*** Chaotic state with multiple explosions ***")
        else:
            print("*** Quasi-stable or transitional state ***")
        
        # Store evolution data
        self.power_evolution = power_evolution
        self.energy_evolution = energy_evolution
        self.pulse_width_evolution = pulse_width_evolution
        self.spectral_width_3db = spectral_width_3db
        self.spectral_width_20db = spectral_width_20db
        
        # Final dashboard update
        if enable_dashboard:
            self.viz.update_dashboard(ii, uout, power_evolution, energy_evolution, 
                                    self.u_z, self.spec_z)
            
            # Show final summary
            input("\nPress Enter to show final summary...")
            self.viz.show_final_summary(ii, uout, power_evolution, energy_evolution)
        
        return u, uout, ii
    
    def close_visualization(self):
        """Close all visualization windows"""
        self.viz.close_all()

def main():
    """Main function to run ANDi laser simulation"""
    sim = ANDiFiberLaserSimulation()
    
    try:
        # Start with stable filter bandwidth (20 nm as in paper)
        filter_bw = 20  # nm
        
        u, uout, iterations = sim.run_simulation(
            filter_bandwidth=filter_bw,
            enable_dashboard=True, 
            update_frequency=25
        )
        
        return sim, u, uout, iterations
        
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user")
        sim.close_visualization()
        return None, None, None, None
    except Exception as e:
        print(f"Simulation error: {e}")
        sim.close_visualization()
        return None, None, None, None

if __name__ == "__main__":
    sim, u, uout, iterations = main()
    
    if sim is not None:
        input("\nPress Enter to close all windows...")
        sim.close_visualization()
