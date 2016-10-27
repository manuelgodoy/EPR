from scipy.signal import argrelextrema
import numpy as np

def amplitude(signal):
    """signal must be a np array"""

    # for local maxima
    indices_max = argrelextrema(signal, np.greater)

    # for local minima
    indices_min = argrelextrema(signal, np.less)

    maxima = signal[indices_max[0]].max()
    minima = signal[indices_min[0]].min()

    return maxima - minima
