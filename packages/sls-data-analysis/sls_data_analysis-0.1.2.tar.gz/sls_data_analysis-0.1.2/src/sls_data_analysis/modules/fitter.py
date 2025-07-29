import os
import numpy as np


from scipy.optimize import curve_fit
from multiprocessing import Pool

from . import istarmap
from .h5_parser import get_scan_data


def fit_function(x, a, b, c):
    return a + b * (np.cos(2*x + c)) ** 2

def fit_count_phi(phi, signal):
    """
    Fit A/D count data vs φ (at 1 wavelength and 1 goniometer angle) using scipy.curve_fit.

    Parameters
    ----------
    phi : array_like
        The sequence of polarizer angles in degrees.
    signal : array_like
        The array containing A/D count values for all polarizer angles.
        len(signal) must be the same as len(phi).

    Returns
    -------
    params : array
        Array of a, b, c fit parameters obtained according to the fitting function.
    """
    try:
        params, _ = curve_fit(fit_function, phi * np.pi / 180, signal, bounds=([0, 0, -np.pi/2], [65536, 65536, np.pi/2]))
        return params  # type = np.array

    except RuntimeError:
        return None, None, None


def fit_at_one_gonio(gonio_index, scan_data):
    """
    Fit at 1 gonio angle along both VV and VH and wavelength

    Returns
    -------
    fit_array: array_like
        fit_array.shape = (2, 2048, 3) TO BE CONFIRMED
    """

    ana = scan_data["ana"]
    phi = scan_data["phi"]
    wl = scan_data["wl"]
    data = scan_data["data"]

    fit_one_gonio_list = []
    for j in range(len(ana)):
        param_list = []
        for k in range(len(wl)):
            params = fit_count_phi(np.array(phi), data[gonio_index, j, :, k])
            param_list.append(params)
        fit_one_gonio_list.append(param_list)
    
    return np.array(fit_one_gonio_list)


def generate_fit_array(scan_data, progress_callback=None):

    theta = scan_data["theta"]

    with Pool(os.cpu_count()-1) as p:
        
        args = [(gonio_index, scan_data) for gonio_index in range(len(theta))]
        counter = 0
        results_list = []

        for result in p.istarmap(fit_at_one_gonio, args):
            results_list.append(result)
            progress_callback.emit(counter) if progress_callback is not None else None
            counter += 1
    
    fit_array = np.array(results_list)

    return fit_array


if __name__ == "__main__":
    # from h5_parser import data_from_h5
    
    import matplotlib.pyplot as plt
    import h5py

    file_path = r"F:/Data/testing/Dataset_20250425_000.h5"

    file = h5py.File(file_path, 'a')

    index = 0

    selected_scan = file[f"RawData/Scan{index:03}"]

    _, scan_data = get_scan_data(selected_scan)

    generate_fit_array(scan_data)
