import numpy as np
from optical_functions import filter_gaussian, coupler, saturable_absorber
from propagation_solver import FiberPropagationSolver

class LaserDesigns:
    def __init__(self, components, sim_params):
        self.components = components
        self.sim_params = sim_params
        self.solver = FiberPropagationSolver(sim_params)
        
    def design_andi_laser(self, u, dplot=0):
        """
        All-Normal Dispersion (ANDi) fiber laser design from the paper
        Cavity: YDF -> SMF1 -> Output Coupler -> SA -> SMF2 -> Filter -> back to YDF
        """
        dt = self.sim_params.dt
        dz = self.sim_params.dz
        fo = self.sim_params.fo
        tol = self.sim_params.tol
        df = self.sim_params.df
        
        # 1. Ytterbium-doped fiber (YDF) - gain section
        u, _, _ = self.solver.ginzburg_landau_propagation(u, dt, dz, self.components.ydf, fo, tol)
        
        # 2. SMF1 - 1m passive fiber after gain
        u, _, _ = self.solver.ginzburg_landau_propagation(u, dt, dz, self.components.smf1, fo, tol)
        
        # 3. Output coupler (25% output)
        u, uout = coupler(u, np.zeros_like(u), self.components.output_coupling)
        
        # 4. Saturable Absorber (SA)
        u = saturable_absorber(u, 
                              self.components.SA['modulation_depth'],
                              self.components.SA['saturation_power'])
        
        # 5. SMF2 - 5m passive fiber before filter
        u, _, _ = self.solver.ginzburg_landau_propagation(u, dt, dz, self.components.smf2, fo, tol)
        
        # 6. Gaussian spectral filter
        u = filter_gaussian(u, 
                           self.components.filter['f3dB'],
                           self.components.filter['fc'],
                           fo, df)
        
        return u, uout
    
    # Keep legacy design for compatibility
    def design_nolm(self, u, dplot=0):
        """Legacy NOLM design - redirects to ANDi"""
        return self.design_andi_laser(u, dplot)
    
    def design_sa(self, u, dplot=0):
        """Legacy SA design - redirects to ANDi"""
        return self.design_andi_laser(u, dplot)
