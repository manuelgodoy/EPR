from scipy.signal import argrelextrema, savgol_filter
import datetime
import numpy as np
import pandas as pd

def SW_clean(signal):
    """Function to filter the signal from the sensorwise output"""
    data = signal['Megnet Control(V)'].duplicated() == False
    aja = []
    for i in xrange(len(signal[data].index.values)-1):
        aja.append(signal['I (uV)'][signal[data].index.values[i]:signal[data].index.values[i+1]-1].mean())
    return np.array(aja)

class EPR(object):
    """This is an object for the EPR signal, the EPR Signal must be a list """
    def __init__(self, signal):
        self.signal = np.array(signal)
        self.time = datetime.datetime.now().strftime("%B %d %Y %H:%M:%S")
        self.maxima = self._set_maxima()
        self.minima = self._set_minima()
        self.amplitude = self._set_amplitude()

    def _set_maxima(self):
        # for local maxima
        indices_max = argrelextrema(self.signal, np.greater)
        self.maxima = self.signal[indices_max[0]].max()
        return self.maxima

    def _set_minima(self):
        # for local minima
        indices_min = argrelextrema(self.signal, np.less)
        self.minima = self.signal[indices_min[0]].min()
        return self.minima

    def _set_amplitude(self):
        self.amplitude = self.maxima - self.minima
        return self.amplitude

    def set_voltage_vector(self, voltage):
        self.voltage = np.array(voltage)
        return

    def set_bfield_vector(self, bfield):
        self.bfield = np.array(bfield)
        return

    def peaks(self):
        """signal must be a np array"""

        if not hasattr(self, 'maxima'):
            self.set_maxima()
        if not hasattr(self,'minima'):
            self.set_minima()

        return self.maxima, self.minima

    def mid_point_index(self):
        # maxima, minima = peaks(signal)
        if not hasattr(self, 'maxima') and not hasattr(self,'minima'):
            self.set_maxima()
            self.set_minima()
        max_ind = np.where(self.signal == self.maxima)[0][0]
        min_ind = np.where(self.signal == self.minima)[0][0]
        return (max_ind+min_ind)/2
        # return None

    def noise(self):
        """This functions takes 5 measurements away from the EPR signal and
        measures their std dev. A phase difference at the mixer may skey this value
        """
        return self.signal[:5].std()

    def s_filter(self, window = 19, polynomial = 9):
        # self.signal = savgol_filter(self.signal, window, polynomial)
        return savgol_filter(self.signal, window, polynomial)

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
    return abs((max_ind+min_ind)/2)
