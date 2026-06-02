phase_out = phase(uout);
delta_w = diff(phase_out);
Eout = abs(uout).^2;
[uout_max,I_uout_max] = max(Eout);
[width,~,~] = fwhm(Eout);
[~,I_l,I_r] = fwzm(Eout,1e-4);
range = I_l:I_r;

figure(3);[ax,p1,p2] = plotyy(t,Eout,t(range),delta_w(range),'plot','plot');
grid on; axis(ax(1),'tight');
axis(ax(2),[min(t),max(t),-2,2]);
xlabel (['t (ps)',sprintf(', %.1fps',width*dt),...
    sprintf(', %.1fW(Peak)',energy/width/dt),...
    sprintf(', %.1fMHz',RepeatFre/1e6)]);
ylabel (ax(1),'|u(z,t)|^2 (W)');
ylabel(ax(2),'Chirp(THz)') % label right y-axis


%Filed output
figure(4),pcolor(t,1:ii,abs(u_z(1:ii,:)).^2);
colorbar;
axis tight;
shading flat;
ylabel ('Round Trip');
xlabel ('t (ps)');
zlabel ('|u(z,t)|^2 (W)');
title ('Output Optical Field Evolution');
view(0,90);

%Filed spectrum
figure(5),pcolor(c./(f + fo),1:ii,spec_z(1:ii,:));
colorbar;
axis tight;
shading flat;
ylabel ('Round Trip');
xlabel ('lambda (nm)');
zlabel ('Normalized Spectrum (a.u.)');
title ('Output Spectrum Evolution');
view(0,90);

AC = xcorr(Eout,Eout);
AC = AC/max(AC);
figure(6),plot(-time+dt:dt:time-dt,AC);
xlabel ('Time Delay (ps)');
ylabel ('AC Trace(a.u.)');

figure(7)
view(30,40)
plot3(Cl,t,abs(u_z(1:ii,:)).^2)
grid on 
xlabel('Round Trip')
ylabel('t (ps)')
zlabel('|u(z,t)|^2 (W)')
title ('3D evo view');
axis square
