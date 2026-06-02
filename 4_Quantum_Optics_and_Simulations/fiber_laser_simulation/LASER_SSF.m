%Split step fourier beam propogtion method algo

function y = LASER_SSF (x, alpha, beta, gamma, Ts, d, h)

x = x(:);

N = floor(d/h);
for idx = 1:N
    if idx == 1
        % Calculate linear part for h/2
        x = fiberDisp(x, alpha, beta, Ts, h/2);
        % Calculate non-linear part for h
        x = fiberNL(x, gamma, h);
    else
        % Calculate linear part for h
        x = fiberDisp(x, alpha, beta, Ts, h);
        % Calculate non-linear part for h
        x = fiberNL(x, gamma, h);
    end
end

% Calculate linear part for h/2
x = fiberDisp(x, alpha, beta, Ts, h/2);
    
y = x;
end

function y = fiberDisp(x, alpha, beta, Ts, h)
xf = fftshift(fft(x));
dw = 2*pi/(Ts*length(x));
w = (-pi/Ts:dw:pi/Ts-(2*pi/80))';
xf = exp(-1j*beta(1)*w*h...
    +1j*beta(2)/2*w.^2*h...
    -1j*beta(3)/6*w.^3*h...
    -alpha/2*h).*xf;
y = ifft(ifftshift(xf));
end

function y = fiberNL(x, gamma, h)
y = exp(1j*gamma*abs(x).^2*h).*x;
end
