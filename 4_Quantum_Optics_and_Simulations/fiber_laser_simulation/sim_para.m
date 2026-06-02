%Simulation parameters
c = 299792.458;         % speed of light nm/ps
lx = 1050;              % wavelength in (nm) (changer here)
lambda_pulse = lx;      % pulse central lambda (nm)
fo=c/lambda_pulse;      % central pulse frequency (THz)

% Numerical Parameters
nt = 2^12;                              % number of spectral points
time = 120;                            	% ps
dt = time/nt;                           % ps
t = -time/2:dt:(time/2-dt);             % ps
df=1/(nt*dt);                           % frequencies separation (Thz)
f=-(nt/2)*df:df:(nt/2-1)*df;            % frequencies vector (en THz)
lambda = c./(f + c/lambda_pulse);    	% lambdas vector (nm)
w = 2*pi*f;                             % angular frequencies vector (in THz)
dz = 0.00001;                        	% Initial longitudinal step (km)
tol = 1e-7;                             % Relative photon error

N_trip = 1000;                         % number of round trips
