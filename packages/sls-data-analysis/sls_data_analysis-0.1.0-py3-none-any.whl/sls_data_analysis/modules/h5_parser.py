import h5py
import json
import numpy as np

def get_scan_count(file):

    scan_count = len([i for i in file["RawData"] if "Scan" in i])  # Count the number of scans in the file

    return scan_count


def get_scan_data(scan):

    scan_info = {
        "date": json.loads(scan.attrs["date_time"])["data"][1:-1],
        "author": json.loads(scan.attrs["author"])["data"][1:-1],
        "description": json.loads(scan.attrs["description"])["data"].encode('latin1').decode('unicode_escape')[1:-1],
        "shape": json.loads(scan["Detector000/Data1D/CH00/Data00"].attrs["shape"])["data"],
        "fit_status": "Done" if "Detector000/Data1D/CH00/Fit00" in scan else "Not done",
    }

    scan_data = {
        "theta": np.array(scan["NavAxes/Axis00"]),
        "ana":   np.array(scan["NavAxes/Axis01"]),
        "phi":   np.array(scan["NavAxes/Axis02"]),
        "wl":    np.array(scan["Detector000/Data1D/CH00/Axis00"]),
        "data":  np.array(scan["Detector000/Data1D/CH00/Data00"]),
        "bkg":   np.array(scan.get("Detector000/Data1D/CH00/Bkg00")),  # Use get here in order to avoid errors when value doesn't exist
                                                                       # Return None if it does not exist (useful for background)
        "fit":   np.array(scan.get("Detector000/Data1D/CH00/Fit00")),
    }

    return scan_info, scan_data

if __name__ == "__main__":
    path = r"F:\Users\begon\Lab\SLS\data\20250424\Dataset_20250424_000.h5"
    
    file = h5py.File(path, 'r')
    