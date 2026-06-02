%SAVEALL

set(groot,'defaultFigureVisible','off')

fig(1) = figure(1);
plot (t,abs(uout).^2);axis tight;
grid on;
xlabel ('t (ps)');
ylabel ('|u(z,t)|^2 (W)');
title ('Pulse Shape');



%plot output spectrum
spec = fftshift(fft(uout));
specnorm = spec.*conj(spec);
specnorm = specnorm/max(specnorm);
fig(2) = figure(2);
plot(c./(f + fo),specnorm);axis tight;
grid on;
xlabel ('lambda (nm)');
ylabel ('Normalized Spectrum (a.u.)');
title ('Output Spectrum');




%Filed output
fig(3) = figure(3),pcolor(t,1:ii,abs(u_z(1:ii,:)).^2);
colorbar;
axis tight;
shading flat;
ylabel ('Round Trip');
xlabel ('t (ps)');
zlabel ('|u(z,t)|^2 (W)');
title ('Output Optical Field Evolution');
view(0,90);


%Filed spectrum
fig(4) = figure(4),pcolor(c./(f + fo),1:ii,spec_z(1:ii,:));
colorbar;
axis tight;
shading flat;
ylabel ('Round Trip');
xlabel ('lambda (nm)');
zlabel ('Normalized Spectrum (a.u.)');
title ('Output Spectrum Evolution');
view(0,90);


% phase_out = phase(uout);
% delta_w = diff(phase_out);
% Eout = abs(uout).^2;
% [uout_max,I_uout_max] = max(Eout);
% [width,~,~] = fwhm(Eout);
% [~,I_l,I_r] = fwzm(Eout,1e-4);
% range = I_l:I_r;
% 
% fig(5) = figure(5);[ax,p1,p2] = plotyy(t,Eout,t(range),delta_w(range),'plot','plot');
% grid on; axis(ax(1),'tight');
% axis(ax(2),[min(t),max(t),-2,2]);
% xlabel (['t (ps)',sprintf(', %.1fps',width*dt),...
%     sprintf(', %.1fW(Peak)',energy/width/dt),...
%     sprintf(', %.1fMHz',RepeatFre/1e6)]);
% ylabel (ax(1),'|u(z,t)|^2 (W)');
% ylabel(ax(2),'Chirp(THz)') % label right y-axis



% AC = xcorr(Eout,Eout);
% AC = AC/max(AC);
% fig(6) = figure(6),plot(-time+dt:dt:time-dt,AC);
% xlabel ('Time Delay (ps)');
% ylabel ('AC Trace(a.u.)');


% fig(6) = figure(6);
% view(30,40)
% plot3(Cl,t,abs(u_z(1:ii,:)).^2)
% grid on 
% xlabel('Round Trip')
% ylabel('t (ps)')
% zlabel('|u(z,t)|^2 (W)')
% title ('3D evo view');
% axis square

M = lambda_bw;
str = string(lambda_bw);
str2 = string(Poffset);
old = '.';
new = '_';
newStr = strrep(str,old,new);
newStr2 = strrep(str2,old,new);

C = {'1','2','3','4'};

for k = 1:4
    F = sprintf('SABP%s_Pin%s_%s', newStr,newStr2,C{k})
    savefig(fig(k),F)
end

for k = 1:4
    F = sprintf('SABP%s_Pin%s_%s.jpg', newStr,newStr2,C{k})
    saveas(fig(k),F)
end
