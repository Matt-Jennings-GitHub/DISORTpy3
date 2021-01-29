import _py3disort

def call_disort(num_layers, phase_moments, dtau=[0.1], w0=[0.95], max_moments=0,
                temps=[270.0,270.0], num_streams=32,
                zen_angles=[-1.0,-0.5,0.5,1.0], azi_angles=[0.0], beam_intensity=1.0,
                surface_albedo=0.1, accur=1e-8):
    
    import numpy as np
    def param_error(message):
        print("Parameter Error : {}".format(message))
        return 0
    
    ## Setup Variables ##
    
    ## Vertical Profile

    # nlyr
    try:
        nlyr = int(num_layers)
    except:
        return param_error("Could not convert number of layers to int")
    
    # nmom
    try:
        if not max_moments and hasattr(phase_moments, '__iter__'): 
            max_moments = len(phase_moments[0])
            nmom = max_moments - 1  
        else:
            max_moments = int(max_moments)
            nmom = max_moments -1 
        if max_moments < 20 :
            return param_error("Please use a minimum of 20 phase moments")
    except:
        return param_error("Could not convert number of moments to int")

    # pmom
    try:
        pmom = np.array(phase_moments,dtype='float')
        pmom = pmom[:, :max_moments] 
        if pmom.shape[0] != num_layers :
            return param_error("Phase moments dimension 0 (Layers) mismatch")
        if pmom.shape[1] != max_moments:
            return param_error("Phase moments dimension 1 (Number of moments) mismatch")
        if pmom[:,0] != np.ones(num_layers):
            return param_error("First phase moment al all layers must be 1.0")
        
        pmom = np.swapaxes(pmom,0,1)
    except:
        return param_error("Could not convert phase moments to 2D float array")
    
    # dtauc
    try:
        dtauc = np.array(dtau,dtype='float')
        if len(dtauc) != nlyr:
           return param_error("dtauc dim mismatch")
    except:
        return param_error("Could not convert dtau to float array")

    # ssalb
    try:
        ssalb = np.array(w0,dtype='float')
        if len(w0) != nlyr:
            return param_error("w0 dim mismatch")
    except:
        return param_error("Could not convert w0 to float array")
    
    
    # temper 
    try:
        temper = np.array(temps, dtype='float')
        if len(temper) != nlyr + 1:
           return param_error("temp Dimension Mismatch (Specified at levels, not layers, top level in temp[0]")
    except:
        return param_error("Could not convert temps to float array")
    
    
    ## Output Positions
    
    # usrtau 
    usrtau = True
    
    # utau 
    utau = np.array([dtauc[0]])

    # ntau 
    ntau = len(utau)
    
    ## Output Angles
    
    #usrang
    usrang = True
    
    # umu
    try:
        umu = np.array(zen_angles,dtype='float')
    except:
        return param_error("Could not convert zentih angles to rank-1 float array")
    
    # numu 
    numu = len(umu)

    # phi
    try:
        phi = np.array(azi_angles,dtype='float')
    except:
        return param_error("Could not convert azimuth angles to rank-1 float array")
    
    # nphi 
    nphi=len(phi)

    # umu0 
    umu0=1.0
    
    # phi0
    phi0=0.0

    ## Surface
    
    #ibcnd
    ibcnd=0

    # lamber 
    lamber=True
    
    # fbeam 
    try:
        fbeam = float(beam_intensity)
    except:
        return param_error("Could not conver beam intensity to float")

    # albedo 
    try:
        albedo = float(surface_albedo)
    except:
        return param_error("Could not conver surface albedo to float")

    ## Efficiency
    
    # nstr 
    try:
        nstr = int(num_streams)
    except:
        return param_error("Could not convert number of streams to int")

    ## OTHERS
    
    # fisot 
    fisot=0.0
                           
    # plank 
    plank = False
    
    # btemp
    btemp=0.0
    # ttemp
    ttemp=0.0
    # temis 
    temis=0.0
                           
    # wvnmlo 
    wvnmlo=0.0
    # wvnmhi
    wvnmhi=0.0
    
    # onlyfl 
    onlyfl=False

    # prnt
    prnt=np.array([False,False,False,False,False])
    
    # header 
    header = ''

  

    ## Call DISORT ##

    rfldir, rfldn, flup, dfdt, uavg, uu, albmed, trnmed = \
            _py3disort.disort(nlyr, dtauc, ssalb, nmom, pmom,
                temper, wvnmlo, wvnmhi, usrtau, ntau, utau,
                nstr, usrang, numu, umu, nphi, phi, ibcnd, fbeam,
                umu0, phi0, fisot, lamber, albedo, btemp, ttemp, temis, plank,
                onlyfl, accur, prnt, header)
    
    return rfldir, rfldn, flup, dfdt, uavg, uu, albmed, trnmed

