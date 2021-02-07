import _py3disort

def call_disort(num_layers, phase_moments, dtau=[0.1], w0=[0.95], max_moments=0,
                temps=[270.0,270.0], num_streams=32,
                zen_angles=[-1.0,-0.5,0.5,1.0], azi_angles=[0.0], sol_zen_angle = 1.0, beam_intensity=1.0,
                surface_albedo=0.1, accur=1e-8):
    """
    Performs radiative transfer simulations in a user-specified atmosphere by calling the fortran DISORT radiative transfer code.

    Parameters
    ---------------
    num_layers: int
        Number of user-specificed layers in the atmosphere
            
    phase_moments: float, array dim(num_layers, number of coefficients for the layer's phasefunction)
        The scattering phase function at each layer, expressed as an array of coefficient arrays, of the legendre polynomial expansion of each layer's phase function

    dtau: float, array len(num_layers)
        Optical thickness at each layer (Default: [0.1] )
    w0: float, array
        Single scatter albedo at each layer (Default: [0.95] )
        
    max_moments: int
        Maximum number of legendre coefficients to inlcude (Default: shape(phase_moments)[1])
        
    temps: float, array len(num_layers + 1)
        Temperature of each layer including the surface
    num_streams: int >=2 and even
        Number of computational polar angles to be used for calculations (Default: 32)

    zen_angles: float, array
        Cosine of viewing zenith angles where to output the RT fields, in increasing order (Default: [-1.0,-0.5,0.5,1.0])

    azi_angles: float, array
        Viewing azimuth angles where to output the RT fields, in degrees (Default: [0.0])
    
    sol_zen_angle: float
        Cosine of the solar zenith angle (Default: 1.0)

    beam_intensity: float
        Solar irradiance (Default: 1.0)

    surface_albedo: float
        Surface albedo (Default: 0.1)

    accur: float
        Convergence criterion for azimuthal (Fourier cosine) series. See 'Docs' for more info. (Default: 1e-8)
    
        
    Returns
    ---------------
    ds_fields : list of arrays
        [rfldir, rfldn, flup, dfdt, uavg, uu, albmed, trnmed]

        rfldir : Downward Direct
        rfldn  : Downward Diffuse
        flup   : Upward Diffuse
        dfdt   : d(Net Flux) / d(Op Dep)
        uu     : Intensity
        uavg   : Mean intensity (including the direct beam)
                 (Not corrected for delta-M-scaling effects)
        albmed : Albedo of the medium as a function of incident
                 beam angle cosine UMU(IU)  (IBCND = 1 case only)
        trnmed : Transmissivity of the medium as a function of incident
                 beam angle cosine UMU(IU)  (IBCND = 1 case only)

    """

    import numpy as np
    def param_error(message):
        print("Parameter Error : {}".format(message))
        return None

    ## Setup Variables ##

    ## Vertical Profile

    # nlyr # Number of layers
    try:
        nlyr = int(num_layers)
    except:
        return param_error("Could not convert number of layers to int")

    # num_moms # Number of moments
    try:
        if not max_moments and hasattr(phase_moments, '__iter__'): # Take default max moms as number given
            max_moments = len(phase_moments[0])
            nmom = max_moments - 1  # FIRST COEFFICIENT ALWAYS 1, nmom is number of extra
        else:
            max_moments = int(max_moments)
            nmom = max_moments -1 # FIRST COEFFICIENT ALWAYS 1, nmom is number of extra
        if max_moments < 20 :
            return param_error("Please use a minimum of 20 phase moments")
    except:
        return param_error("Could not convert number of moments to int")

    # pmom:  # Phase function at each layer
    try:
        pmom = np.array(phase_moments,dtype='float')
        pmom = pmom[:, :max_moments] # Trim excess moments
        pmom[:,0] = np.round(pmom[:,0],decimals=5) # Round the first moment to 1.00000 in case of slight inaccuracy
        if pmom.shape[0] != num_layers :
            return param_error("Phase moments dimension 0 (Layers) mismatch")
        if pmom.shape[1] != max_moments:
            return param_error("Phase moments dimension 1 (Number of moments) mismatch")
        if not np.array_equal(pmom[:,0], np.ones(num_layers,dtype='float') ):
            return param_error("First phase moment al all layers must be 1.0")

        pmom = np.swapaxes(pmom,0,1) # Reshape before passing
    except:
        return param_error("Could not convert phase moments to 2D float array")

    #dtauc : # Atmosphere optical profile, array
    try:
        dtauc = np.array(dtau,dtype='float')
        if len(dtauc) != nlyr:
           return param_error("dtauc dim mismatch")
    except:
        return param_error("Could not convert dtau to float array")

    #ssalb: Single scatter albedo, array
    try:
        ssalb = np.array(w0,dtype='float')
        if len(w0) != nlyr:
            return param_error("w0 dim mismatch")
    except:
        return param_error("Could not convert w0 to float array")


    #temper: Layer and surface temperatures
    try:
        if temps == [270.0, 270.0]: # Replace default value
            temps = [270.0]*(num_layers+1)
        temper = np.array(temps, dtype='float')
        if len(temper) != nlyr + 1:
           return param_error("temp Dimension Mismatch (Specified at levels, not layers, top level in temp[0]")
    except:
        return param_error("Could not convert temps to float array")


    ## Output Positions

    #usrtau True => Return properties at utau, which is set as the top-of-atmosphere optical depth
    usrtau = True

    #utau: Optical depths to return RT feilds, set as top layer optical depth
    utau = np.array([dtauc[0]])

    #ntau: length of utau 
    ntau = len(utau)

    ## Output Angles

    #usrang: specify angles to return RT feilds
    usrang = True

    #umu : Cosine of zenith polar angles, in increasing order
    try:
        umu = np.array(zen_angles,dtype='float')
    except:
        return param_error("Could not convert zenith angles to rank-1 float array")

    #numu: length of umu
    numu = len(umu)

    #phi: Azimuth angles to return beam, in degrees
    try:
        phi = np.array(azi_angles,dtype='float')
    except:
        return param_error("Could not convert azimuth angles to rank-1 float array")

    #nphi: length of phi
    nphi=len(phi)

    #umu0: Cosine of incident beam angle 

    try:
        umu0 = float(sol_zen_angle)
    except:
        return param_error("Could not convert solar zenith angles to float")

    #phi0 Azimuth of incident beam DEFAULT = 0.0
    phi0=0.0

    ## Surface

    #ibcnd DEFAULT 0 (Use default surface boundry conditions)
    ibcnd=0

    #lamber DEFAULT = True (Isotropic or bidirection bottom boundry)
    lamber=True

    #fbeam: Solar irradiance
    try:
        fbeam = float(beam_intensity)
    except:
        return param_error("Could not conver beam intensity to float")

    #albedo: Bottom boundry albedo
    try:
        albedo = float(surface_albedo)
    except:
        return param_error("Could not conver surface albedo to float")

    ## Efficiency

    #nstr: number of streams
    try:
        nstr = int(num_streams)
    except:
        return param_error("Could not convert number of streams to int")

    ## OTHERS

    #fisot: Reflection at top boundry
    fisot=0.0

    #plank: REMOVED Don't use plank function or it's conditions (Thermal wavelengths)
    plank = False

    #btemp REMOVED
    btemp=0.0
    #ttemp REMOVED
    ttemp=0.0
    #temis REMOVED
    temis=0.0

    #wvnmlo REMOVED
    wvnmlo=0.0
    #wvnmhi REMOVED
    wvnmhi=0.0

    #onlyfl , False: return all flux and intensity qutities
    onlyfl=False

    #prnt REMOVED
    prnt=np.array([False,False,False,False,False])

    #header REMOVED
    header = ''

    ## Make Call ##
    '''
    print("Final Params: ",nlyr, dtauc, ssalb, nmom, pmom,
                temper, wvnmlo, wvnmhi, usrtau, ntau, utau,
                nstr, usrang, numu, umu, nphi, phi, ibcnd, fbeam,
                umu0, phi0, fisot, lamber, albedo, btemp, ttemp, temis, plank,
                onlyfl, accur, prnt, header,sep="\n")
    '''

    rfldir, rfldn, flup, dfdt, uavg, uu, albmed, trnmed = \
            _py3disort.disort(nlyr, dtauc, ssalb, nmom, pmom,
                temper, wvnmlo, wvnmhi, usrtau, ntau, utau,
                nstr, usrang, numu, umu, nphi, phi, ibcnd, fbeam,
                umu0, phi0, fisot, lamber, albedo, btemp, ttemp, temis, plank,
                onlyfl, accur, prnt, header)

    return rfldir, rfldn, flup, dfdt, uavg, uu, albmed, trnmed
