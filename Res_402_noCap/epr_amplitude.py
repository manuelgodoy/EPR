from scipy.signal import argrelextrema
import numpy as np

def peaks(signal):
    """signal must be a np array"""

    # for local maxima
    indices_max = argrelextrema(signal, np.greater)

    # for local minima
    indices_min = argrelextrema(signal, np.less)

    maxima = signal[indices_max[0]].max()
    minima = signal[indices_min[0]].min()

    return maxima, minima

def amplitude(signal):
    maxima, minima = peaks(signal)
    return maxima - minima

def mid_point_index(signal):
    maxima, minima = peaks(signal)
    max_ind = np.where(signal == maxima)[0][0]
    min_ind = np.where(signal == minima)[0][0]
    return abs((max_ind-min_ind)/2)
