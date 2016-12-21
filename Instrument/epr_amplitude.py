from scipy.signal import argrelextrema, savgol_filter
import datetime
import numpy as np
import pandas as pd
import sys

def SW_clean(signal):
    """Function to filter the signal from the sensorwise output"""
    data = signal['Megnet Control(V)'].duplicated() == False
    aja = []
    for i in xrange(len(signal[data].index.values)-1):
        aja.append(signal['I (uV)'][signal[data].index.values[i]:signal[data].index.values[i+1]-1].mean())
    return np.array(aja)

def SW_width(signal):
    """Function to filter the signal from the sensorwise output"""
    data = signal['Megnet Control(V)'].duplicated() == False
    df = pd.DataFrame()
    epr_signal = []
    magnetic_field = []
    for i in xrange(len(signal[data].index.values)-1):
        epr_signal.append(signal['I (uV)'][signal[data].index.values[i]:signal[data].index.values[i+1]-1].mean())
        magnetic_field.append(signal['Megnet Control(V)'][signal[data].index.values[i]])
    df['EPR'] = np.array(epr_signal)
    df['Field'] = np.array(magnetic_field)
    return df

def analysis(sample):
    import glob
    data = []
    main_path = "/Users/manuelgodoy/Dropbox/Projects/Cenovus Weyburn Trials/Data/"
    path = "/Users/manuelgodoy/Dropbox/Projects/Cenovus Weyburn Trials/Data/*_{0}.csv".format(sample)
    df = pd.DataFrame()
    for filename in glob.glob(path):
        # print filename
        d = pd.read_csv(filename)
        d_clean = EPR(SW_clean(d))
        d_filtered = EPR(d_clean.s_filter())
        data.append(d_filtered)
        df[filename.strip(main_path)] = d_filtered.removeDC()

    average = []
    for i in data:
        average.append(i.amplitude)

    df['Vpp Average'] = pd.DataFrame(average).mean()
    df['Error'] = pd.DataFrame(average).std()

    df.to_csv("/Users/manuelgodoy/Dropbox/Projects/Cenovus Weyburn Trials/Data/{0}.csv".format(sample), index = False)
    return sum(average)/float(len(average))


class EPR(object):
    """This is an object for the EPR signal, the EPR Signal must be a list """
    def __init__(self, signal, magnetic_field = None):
        self.signal = np.array(signal)
        self.time = datetime.datetime.now().strftime("%B %d %Y %H:%M:%S")
        self.magnetic_field = magnetic_field
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
        self.signal_filtered = savgol_filter(self.signal, window, polynomial)
        return savgol_filter(self.signal, window, polynomial)

    def removeDC(self):
        m = self.signal.mean()
        self.signal_no_DC = self.signal - m
        return self.signal_no_DC

    def width(self):
        max_ind = np.where(self.signal == self.maxima)[0][0]
        min_ind = np.where(self.signal == self.minima)[0][0]
        self.width_ = np.abs(self.magnetic_field[max_ind] - self.magnetic_field[min_ind])
        return self.width_



if __name__ == "__main__":
    if len(sys.argv) > 1:
        sample = sys.argv[1]
    print analysis(sample)
