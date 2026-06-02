%u->BPF->SMF5m->AMP1m->SMF1m->oc->SA->bpf 
    %BPF
    u_f = filter_gauss(u,filter.f3dB,filter.fc,filter.n,fo,df);
    u = u_f;
    
    %SMF5m
    [u,~,Plotdata_smf7] = LASER_IP_FD(u,dt,dz,smf7,fo,tol,dplot);

    %AMP1m
    [u,~,Plotdata_amf2] = LASER_IP_FD(u,dt,dz,amf2,fo,tol,dplot);

    %SMF1m
    [u,~,Plotdata_smf8] = LASER_IP_FD(u,dt,dz,smf8,fo,tol,dplot);

    %SA
    u = LASER_SA (u,Isa);

     %OC
    [u,uout] = coupler(u,0,rho_out2);
