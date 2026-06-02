function [Eout, Pout] = AmpSimpNonoise(Ein, G, Psat)
    Pin = abs(Ein).^2;
    G = G ./ (1 + Pin ./ Psat);
    Eout = Ein .* sqrt(G);
    Pout = abs(Eout).^2;
end
