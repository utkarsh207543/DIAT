%SA
Isa = 5000;         %saturation intensity (W)

%Parameter 
lambda_bw = 11;     %bandwidth in (nm)


smf5_L = 0.025;     %length in (km)
NOLM_L = 0.0015;    %length in (km)
PsatdBm = 26;     %Pump power in (dBm) 23.5
smf4_L = 0.002;     %length in (km)

% Fiber design structure
PM980.Amod = pi*3.3^2;                  % Mode Field Area (um^2) (um^2)
PM980.n2 = 2.6;                      	% Kerr coefficient (10^-16*cm^2/W)
PM980.gamma = 2*pi*PM980.n2/lambda_pulse/PM980.Amod*1e4;	% W^-1 * km^-1
PM980.alpha = 0;                       	% atenuation coef. (km^-1)
PM980.betaw = [0 0 24.5864 26.1949e-3];	% beta coefficients (ps^n/nm)

PM980.raman = 0;                      	% 0 = exclude raman effect
PM980.ssp = 0;                        	

PM1025 = PM980;
PM1025.Amod = pi*5^2;
PM1025.gamma = 2*pi*PM1025.n2/lambda_pulse/PM1025.Amod*1e4;	% W^-1 * km^-1
PM1025.betaw = [0 0 20.8634 34.9621e-3];

F10125 = PM980;
F10125.Amod = pi*5.25^2;
F10125.gamma = 2*pi*F10125.n2/lambda_pulse/F10125.Amod*1e4;	% W^-1 * km^-1
F10125.betaw = [0 0 20.1814 36.8057e-3];

%NOLM
% smf1 module parameters
NOLM.smf1 = F10125;
NOLM.smf1.L = 0.0007;                       	% fiber length (km)

% smf2 module parameters
NOLM.smf2 = F10125;
NOLM.smf2.L = NOLM_L-NOLM.smf1.L;

% smf3 module parameters
smf3 = F10125;
smf3.L = 0.001;

% smf4 module parameters
smf4 = F10125;
smf4.L = smf4_L; 

% smf5 module parameters
smf5 = F10125;
smf5.L = smf5_L; 

% smf5 module parameters
smf6 = F10125;
smf6.L = 0.001;

% amf1 module parameters
amf1 = F10125;
amf1.L = 0.0008;
amf1.gssdB = 37.5;          % small signal gain coefficient(dB)
amf1.PsatdBm = PsatdBm; 	% saturation input power(dBm)

amf1.fbw = c/(lx)^2*80; 
amf1.fc = c/lx;

%SA
% smf7 module parameters
smf7 = F10125;
smf7.L = 0.005; 

% smf8 module parameters
smf8 = F10125;
smf8.L = 0.001;

% amf2 module parameters
amf2 = F10125;
amf2.L = 0.001;
amf2.gssdB = 37.5;          % small signal gain coefficient(dB)
amf2.PsatdBm = PsatdBm; 	% saturation input power(dBm)

amf2.fbw = c/(lx)^2*80; 
amf2.fc = c/lx;

% filter parameters
filter.lambda_c = lx;
filter.lambda_bw = lambda_bw;
filter.fc = c/filter.lambda_c;
filter.f3dB = c/(filter.lambda_c)^2*filter.lambda_bw;
filter.n = 7;

% coupler parameters
NOLM.rho = 0.30;        % NOLM coupler config  
rho_out = 0.40;         % NOLM design output coupler config
rho_out2 = 0.23;        % For SA design output coupler config
PhaseShift = 0;         % Nonreciprocal phase phift 

%Length_cavity = smf4.L+smf5.L+amf1.L+NOLM.smf1.L+NOLM.smf2.L;      % km NOLM
Length_cavity = smf7.L+smf8.L+amf2.L;                               % km SA
RepeatFre = c/2/Length_cavity;                               	    % Hz
amf1.RepeatFre = RepeatFre;                                         %NOLM
amf2.RepeatFre = RepeatFre;                                         %SA
