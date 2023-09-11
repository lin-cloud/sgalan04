import numpy as np
from ecgImage import ECG_image_values
from ecgSignal import ECG_signal2QRS


#def ecg2parametros(matrix):
def ecg2parametros(file):
    
    ecg, Ts = ECG_image_values(file, draw=False)
    qtc, FC, qtc_times, r_times = ECG_signal2QRS(ecg, Ts, draw=False)
    #res = matrix[0, 0:10]
    return qtc, FC, qtc_times, r_times




 