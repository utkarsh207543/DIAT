%Ring Fiber Laser
%Utkarsh Kumar Singh
%utkarsh@ieee.org
%DRDO DIAT (2022)

%Main Program
close all;
clear all;
clc;

%Parameters Call
sim_para;       %call simulation parameters 
components;     %call components dataset


%Input fields

%A(1,:) = wgn(nt,1,0,'complex'); %Noise seed
%A(1,:) = wgn(N,1,0);
%A(1,:)= rand_sech(nt,time);
%A(1,:) = sqrt(Po)*sech(t/To);
%A1(1,:) = rand_sech(nt,time);
%A2(1,:) = wgn(N,1,0);
%A(1,:) = A1.*A2;
%A(1,:)= rand_sech(nt,time);
u0 = rand_sech(nt,time);    %Noisy sech seed
u = u0;

spec_z = zeros(N_trip,nt);
u_z = spec_z;

dplot = 1;
dstop = 0;


for ii = 1:N_trip
    Cl(1:nt,ii) = ii;
    disp('Round Trip =')
    disp(ii)

    %result
    power = max(u.*conj(u));
    energy = dt*sum(u.*conj(u));

    disp('Peak Power (W) =')
    disp(power)

    disp('Pulse Energy (pJ) =')
    disp(power)  
    

    %CALL DESIGN
    
    %designnolm;   %NOLM design 
    designsa;      %Ring with SA design

    %change cavity length in components as per design
    
    %plot temporal input and output pulses
    figure(1)
    plot (t,abs(uout).^2);axis tight;
    grid on;
    xlabel ('t (ps)');
    ylabel ('|u(z,t)|^2 (W)');
    title ('Pulse Shape');

    %plot output spectrum
    spec = fftshift(fft(uout));
    specnorm = spec.*conj(spec);
    specnorm = specnorm/max(specnorm);
    figure(2)
    plot(c./(f + fo),specnorm);axis tight;
    grid on;
    xlabel ('lambda (nm)');
    ylabel ('Normalized Spectrum (a.u.)');
    title ('Output Spectrum');
    
    spec_z(ii,:) = specnorm;
    u_z(ii,:) = uout;
    
    if dstop
        break;
    end
   
    
    % Check terminating condition
    
     if ii>5
        if max(xcorr_normal(spec_z(ii,:),spec_z(ii-1,:),nt/8))>0.99999
                disp('Convergence..............................')
                dstop = 1; %if convergence end the sim
        end
    end


    %check end
    
end
