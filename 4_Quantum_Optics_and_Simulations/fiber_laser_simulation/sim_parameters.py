import numpy as np

class SimulationParameters:
    def __init__(self):
        # Physical constants
        self.c = 299792.458  # speed of light nm/ps
        self.lx = 1030  # Operating wavelength for Yb laser (nm)
        self.lambda_pulse = self.lx  # pulse central lambda (nm)
        self.fo = self.c / self.lambda_pulse  # central pulse frequency (THz)
        
        # Numerical Parameters
        self.nt = 2**12  # number of spectral points
        self.time = 50  # ps (shorter window for dissipative solitons)
        self.dt = self.time / self.nt  # ps
        self.t = np.linspace(-self.time/2, self.time/2 - self.dt, self.nt)  # ps
        self.df = 1 / (self.nt * self.dt)  # frequencies separation (THz)
        self.f = np.linspace(-(self.nt/2)*self.df, (self.nt/2-1)*self.df, self.nt)  # frequencies vector (THz)
        self.lambda_vec = self.c / (self.f + self.c/self.lambda_pulse)  # lambdas vector (nm)
        self.w = 2 * np.pi * self.f  # angular frequencies vector (THz)
        self.dz = 0.00001  # Initial longitudinal step (km)
        self.tol = 1e-6  # Relative photon error
        
        self.N_trip = 2000  # number of round trips (as in paper)
