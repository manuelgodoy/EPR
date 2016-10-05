from scipy.signal import argrelextrema
import numpy as np

def amplitude(signal):

    # for local maxima
    indices_max = argrelextrema(signal, np.greater)

    # for local minima
    indices_min = argrelextrema(signal, np.less)
