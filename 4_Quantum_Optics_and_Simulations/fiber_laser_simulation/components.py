import numpy as np
from sim_parameters import SimulationParameters

class FiberComponents:
    def __init__(self, sim_params):
        self.sim_params = sim_params
        self.c = sim_params.c
        self.lambda_pulse = sim_params.lambda_pulse
        self.lx = sim_params.lx
        
        # Parameters from the paper
        self.lambda_bw = 20  # Initial filter bandwidth (nm) - from paper
        
        # Fiber lengths from paper
        self.ydf_L = 0.001   # 1m Ytterbium-doped fiber
        self.smf1_L = 0.001  # 1m SMF after YDF
        self.smf2_L = 0.005  # 5m SMF before filter
        
        # Initialize fiber types for 1030 nm Yb laser
        self._init_fibers()
        self._init_components()
    
    def _init_fibers(self):
        # Ytterbium-doped fiber (YDF) parameters from paper
        self.YDF = {
            'Amod': np.pi * 3.0**2,  # Mode field area (um^2)
            'n2': 2.6,  # Kerr coefficient (10^-16*cm^2/W)
            'alpha': 0.0,  # No loss in gain fiber
            'betaw': [0, 0, 22.0, 0.1],  # Normal dispersion β₂ = +22 ps²/km
            'gamma': 5.1,  # Nonlinear coefficient from paper (W^-1 km^-1)
            'raman': 0,  # Disable for initial stability
            'ssp': 0,    # Disable self-steepening initially
            'gain_type': 'yb'  # Ytterbium gain
        }
        
        # Single Mode Fiber (SMF) parameters
        self.SMF = {
            'Amod': np.pi * 5.2**2,  # Standard SMF mode field area
            'n2': 2.6,
            'alpha': 0.2,  # Standard fiber loss (dB/km -> km^-1)
            'betaw': [0, 0, 22.0, 0.1],  # Same dispersion as YDF
            'gamma': 2.0,  # Lower nonlinearity than YDF
            'raman': 0,
            'ssp': 0
        }
    
    def _init_components(self):
        # YDF gain fiber
        self.ydf = self.YDF.copy()
        self.ydf['L'] = self.ydf_L
        self.ydf['name'] = 'YDF'
        self.ydf['lambda_c'] = self.lx
        
        # Gain parameters from paper
        self.ydf['g'] = 6.0  # Small signal gain coefficient (m^-1)
        self.ydf['E_sat'] = 1e-9  # Gain saturation energy (1 nJ)
        self.ydf['gain_bw'] = 40e-9  # Gain bandwidth (40 nm)
        
        # SMF sections
        self.smf1 = self.SMF.copy()
        self.smf1['L'] = self.smf1_L
        self.smf1['name'] = 'SMF1'
        
        self.smf2 = self.SMF.copy()
        self.smf2['L'] = self.smf2_L
        self.smf2['name'] = 'SMF2'
        
        # Saturable Absorber parameters from paper
        self.SA = {
            'modulation_depth': 0.6,  # m parameter
            'saturation_power': 130,  # P_sat (W)
            'type': 'monotonic'  # T1 transfer function
        }
        
        # Output coupler
        self.output_coupling = 0.25  # 25% output coupling from paper
        
        # Gaussian spectral filter parameters
        self.filter = {
            'lambda_c': self.lx,
            'lambda_bw': self.lambda_bw,  # FWHM bandwidth
            'fc': self.c / self.lx,
            'f3dB': self.c / (self.lx)**2 * self.lambda_bw,
            'shape': 'gaussian'
        }
        
        # Calculate cavity parameters
        self.Length_cavity = self.ydf_L + self.smf1_L + self.smf2_L
        self.RepeatFre = self.c / 2 / self.Length_cavity  # Hz
        
        # Legacy parameters for compatibility
        self.Isa = self.SA['saturation_power']
        self.rho_out = self.output_coupling
        self.rho_out2 = self.output_coupling
        
        print(f"All-Normal Dispersion Yb Fiber Laser Configuration:")
        print(f"  Operating wavelength: {self.lx} nm")
        print(f"  Cavity length: {self.Length_cavity*1000:.1f} m")
        print(f"  Repetition rate: {self.RepeatFre/1e6:.2f} MHz")
        print(f"  YDF length: {self.ydf_L*1000:.1f} m")
        print(f"  Total SMF length: {(self.smf1_L + self.smf2_L)*1000:.1f} m")
        print(f"  Filter bandwidth: {self.lambda_bw} nm")
        print(f"  Output coupling: {self.output_coupling*100:.0f}%")
        print(f"  Dispersion: +{self.YDF['betaw'][2]} ps²/km (Normal)")
        print(f"  YDF gamma: {self.YDF['gamma']} W⁻¹km⁻¹")
        print(f"  SA modulation depth: {self.SA['modulation_depth']}")
        print(f"  SA saturation power: {self.SA['saturation_power']} W")
