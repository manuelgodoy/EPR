from scipy.signal import argrelextrema
import datetime
import numpy as np

class EPR(object):
    """This is an object for the EPR signal, the EPR Signal must be a list """
    def __init__(self, signal):
        self.signal = np.array(signal)
        self.time = datetime.datetime.now().strftime("%B %d %Y %H:%M:%S")
        # indices_max = argrelextrema(self.signal, np.greater)
        # self.maxima = self.signal[indices_max[0]].max()
        self.maxima = self.find_maxima(self.signal)
        # indices_min = argrelextrema(self.signal, np.less)
        # self.minima = self.signal[indices_min[0]].min()
        self.minima = self.find_minima(self.signal)
        self.amplitude = self.maxima - self.minima

    # @classmethod
    def find_maxima(self, signal):
        indices_max = argrelextrema(signal, np.greater)
        maxima = self.signal[indices_max[0]].max()
        return maxima

    def find_minima(self, signal):
        indices_min = argrelextrema(signal, np.less)
        minima = self.signal[indices_min[0]].min()
        return minima

    def set_maxima(self):
        # for local maxima
        indices_max = argrelextrema(self.signal, np.greater)
        self.maxima = self.signal[indices_max[0]].max()
        return self.maxima

    def set_minima(self):
        # for local minima
        indices_min = argrelextrema(self.signal, np.less)
        self.minima = self.signal[indices_min[0]].min()
        return self.minima

    # def set_voltage_vector(self, voltage):
    #     self.voltage = np.array(voltage)
    #     return
    #
    # def set_bfield_vector(self, bfield):
    #     self.bfield = np.array(bfield)
    #     return

    def amplitude(self):
        self.amplitude = self.maxima - self.minima
        return self.amplitude

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

    def noise(self, sample_size = 5, from_beginning = True):
        """This functions takes 5 measurements away from the EPR signal and
        measures their std dev. A phase difference at the mixer may skey this value
        """
        if from_beginning:
            return self.signal[:sample_size].std()
        else:
            return self.signal[-sample_size:].std()

    def to_db(self):
        return 10*np.log10(self.signal*self.signal/0.050)
