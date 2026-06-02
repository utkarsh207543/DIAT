function y = LASER_SA (u, Isa)
    p0=50;
    e=0.01;
    I=Isa/5;
    y = u.*((e+(abs(u)).^2/I)./(1+(abs(u)).^2/I)).^0.5;% can be arbitrary functions
end
