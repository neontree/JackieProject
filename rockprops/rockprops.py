import numpy as np
import math


def calculate_ucs(mse, method='pump efficiency', pump_efficiency=0.60):
    """"Calculate unconfined compressive strength from MSE
    method='pump efficiency': based on Joshua Love ref

    Input unit:
        mse: psi

    Output unit:
        ucs: psi
    """
    if method == 'pump efficiency':
        ucs = pump_efficiency * mse
    else:
        raise ValueError('Unknown method.')

    return ucs  #unit: psi


def calculate_ccs(ucs, gr, presdiff, gr_cutoff=65):
    """Calculate confined compressive strength in psi from UCS based on
    https://www-onepetro-org.ezproxy.lib.uh.edu/download/conference-paper/SPE-27034-MS?id=conference-paper%2FSPE-27034-MS

    Input units:
        ucs: psi
        diff_pres: differential pressure, kPa

    Output unit:
        ccs: psi
    """

    ccs = np.zeros(shape=ucs.shape)

    # convert differential pressure from kPa to psi to comply with the correlation
    presdiff = presdiff * 1000 * 14.7 / 101325

    # filter out shale fraction
    shale_mask = gr > gr_cutoff

    ccs[shale_mask] = ucs[shale_mask] * (1 + 0.00432 * presdiff[shale_mask] ** 0.782)
    ccs[~shale_mask] = ucs[~shale_mask] * (1 + 0.0133 * presdiff[~shale_mask] ** 0.577)

    return ccs      #unit: psi


def calculate_youngmodulus(ccs, pc):
    """Calculate Youngmodulus E in Gpa from curve fitting based on lab measurements
        as a function of confined pressure
    Source: http://www.rocsoltech.com/wp-content/uploads/2018/08/Rocsol-DWOB-and-D-ROCK-Presentation.pdf

    Input units:
        ccs: psi
        pc: kPa

    Output unit:
        E: Gpa
    """

    # convert units so they comply to the curve fitting function
    # ccs: Mpa
    # pc: Mpa

    ccs = ccs * 0.101325 / 14.7
    pc = pc / 1000
    #constant from curve fitting based on exponential functional form
    a, b = 4.5396, 0.1926

    E = ccs * a * pc ** b

    return E    #unit: GPa


def calculate_porosity(ucs, gr, method=3, gr_cutoff=65):
    """"Calculate porosity from ucs based on whether or not the formation is sand or shale

    method=1: based on AADE-17-NTCE-134 and http://www.rocsoltech.com/wp-content/uploads/2018/09/Evaluating-Multiple-Methods-to-Determine-Porosity-from-Drilling-Data-AC-SPE-185115-MS-1.pdf
    method=2: based on http://www.rocsoltech.com/wp-content/uploads/2018/09/An-Empirical-Model-to-Estimate-a-Critical-Stimulation-Design-Parameter-Using-Drilling-Data-SPE-185741-MS.pdf
    method=3: curve fitting based on method 2 by curve fitting GR as well (so we dont have to worry about GR cutoff
        but I didn't find the unit for GR in this eq. I assume it is field unit which is API

    Input unit:
        ucs: psi
    Output unit:
        porosity: fraction"""

    # convert ucs from psi to Mpa
    ucs = ucs * .101325 / 14.7

    porosity = np.zeros(shape=ucs.shape)

    # filter out shale fraction
    shale_mask = gr > gr_cutoff
    if method == 1:
        # convert ucs from psi to MPa
        ucs = ucs * 101.325 / 14.7

        # constant
        # for shale
        k1, k2 = 92.529, -0.63
        # for non-shale
        k3, k4 = 424.8, -0.825

    elif method == 2:
        # convert ucs from psi to MPa
        ucs = ucs * 101.325 / 14.7

        # constant
        # for shale
        k1, k2 = 88.331, -0.636
        # for non-shale
        k3, k4 = 256.25, -0.788
    elif method == 3:
        return 1.75 / (gr ** 0.25 * ucs ** 0.47)

    else:
        raise ValueError('Unknown method.')

    porosity[shale_mask] = (k1 * ucs[shale_mask] ** k2)
    porosity[~shale_mask] = (k3 * ucs[~shale_mask] ** k4)

    return porosity/100


def calculate_permeability(porosity, method=1):
    """Calculate permeability from porosity
    This is tied to method 1 from porosity calculation and is more relevant to Eagle Ford shale (AADE-17-NTCE-134)
    Return
        permeability: nD
    """
    if method == 1:
        permeability = 6.93 * (porosity * 100) ** 2.5313

    return permeability


def calculate_mse(wob, area, rpm, torque, rop):
    """"
    Calculate MSE according to https://www.osti.gov/servlets/purl/1060223, Eq. 5 page 10
        at every depth
    Expect inputs to be in
    Note that the inputs of this equation follows field units
        wob: kDaN
        area: in^2
        rpm: evolution per minute
        torque: in.lbf
        rop: ft/hr

    Return:
    - MSE: in psi
    """

    # convert ROP from ft/hr to in/min
    # convert WOB from kDaN to lbf
    # needed for unit consistency
    rop = rop * 12 / 60
    wob = wob * 1000 * 2.2480894387096
    mse = wob / area + 2 * math.pi * rpm * torque / (area * rop)

    return mse


if __name__ == '__main__':

    from utils import get_filtered_log_reading_dict, merge_logs
    from rockprops.pressures import *

    las_file_1 = r'../input_template/Middleton Unit B 47-38 No. 8SH__From EDR.las'
    logs_reading_dict1, logs_values1 = get_filtered_log_reading_dict(las_file_1)
    las_file_2 = r'../input_template/LAS Middleton Unit B 47-38 No. 8SH_From MWD.las'
    logs_reading_dict2, logs_values2 = get_filtered_log_reading_dict(las_file_2)
    all_logs_reading_dicts = [logs_reading_dict1, logs_reading_dict2]
    all_logs_values = [logs_values1, logs_values2]

    logs_dict, logs_values = merge_logs(all_logs_reading_dicts, all_logs_values, primary_key='TVD')
    gr = logs_dict['GR']
    wob = logs_dict['WOB']
    area = 6
    rpm = logs_dict['RPM']
    torque = logs_dict['TOR']
    rop = logs_dict['ROP']
    diff_pres = logs_dict['DIFP']
    depth = logs_dict['TVD']

    # calculate pressure
    mudweight = 8.95 #ppg
    Phyd = hydsta_pres(mudweight, depth) #KPa
    Pc = conf_pres(Phyd, mudweight)

    # calculate different rock properties
    mse = calculate_mse(wob, area, rpm, torque, rop)
    ucs = calculate_ucs(mse)
    porosity = calculate_porosity(ucs, gr, method=3)
    permeability = calculate_permeability(porosity, method=1)

    ccs = calculate_ccs(ucs, gr, diff_pres)
    E = calculate_youngmodulus(ccs, Pc)
    print(porosity)

    # print(ccs)
    # print(ucs)
    # print(E)
