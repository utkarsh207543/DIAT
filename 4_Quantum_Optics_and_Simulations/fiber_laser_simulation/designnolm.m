%u->BPF->SMF4->AMF1->SMF5->NOLM->OC->u
    u_f = filter_gauss(u,filter.f3dB,filter.fc,filter.n,fo,df);
    u = u_f;
    
    [u,~,Plotdata_smf4] = LASER_IP_FD(u,dt,dz,smf4,fo,tol,dplot);
    [u,~,Plotdata_amf1] = LASER_IP_FD(u,dt,dz,amf1,fo,tol,dplot); 
    [u,~,Plotdata_smf5] = LASER_IP_FD(u,dt,dz,smf5,fo,tol,dplot);
    
    [uf,ub] = coupler(u,0,NOLM.rho);
    % forward light cp1o-smf1-NRPS-smf2-cp2o
    [ufo,~,Plotdata_smf1_f] = LASER_IP_FD(uf,dt,dz,NOLM.smf1,fo,tol,dplot);
     ufo = ufo.*exp(1i*PhaseShift);
    [ufo,~,Plotdata_smf2_f] = LASER_IP_FD(ufo,dt,dz,NOLM.smf2,fo,tol,dplot);
    % forward light cp1o-smf1-NRPS-smf2-cp2o
    [ubo,~,Plotdata_smf1] = LASER_IP_FD(ub,dt,dz,NOLM.smf2,fo,tol,dplot);
     ubo = ubo.*exp(-1i*PhaseShift);
    [ubo,~,Plotdata_smf2] = LASER_IP_FD(ubo,dt,dz,NOLM.smf1,fo,tol,dplot);
    
    [ur,ut] = coupler(ubo,ufo,NOLM.rho);

    u = ut;  
    [u,uout] = coupler(u,0,rho_out);
