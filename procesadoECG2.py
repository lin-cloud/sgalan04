import numpy as np


def ecg2parametros(file):
    qtc = np.random.uniform(0.4, 0.55)
    FC = np.random.uniform(60, 105)
    qtc_times = []
    r_times = []
    return qtc, FC, qtc_times, r_times
