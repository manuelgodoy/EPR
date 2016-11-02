import visa
import sys, csv, time, datetime, math
import numpy as np
from math import pi
import matplotlib.pyplot as plt
# from voltages import voltages
from plotly_settings import s_1, s_2

NUMBER_OF_POINTS = 60
RESOLUTION = 0.0005
VOLTAGE_START = 0.69
TIME_CONSTANT = '3s'
MODULATION_FREQUENCY = '200000'
WAIT_TIME = 0.5

# sensitivity = ['2e-9','5e-9','10e-9','20e-9','50e-9','100e-9','200e-9','500e-9','1e-6',
#                 '2e-6','5e-6','10e-6','20e-6','50e-6','100e-6','200e-6','500e-6','1e-3',
#                 '2e-3','5e-3','10e-3','20e-3','50e-3','100e-3','200e-3','500e-3','1']
sensitivity = [-127,-117,-107,-97,-87,-77,-67,-57,-47,-37,-27,-17,-7,3,13]
time_constants = ['100us','300us','1ms','3ms','10ms','30ms','100ms','300ms',
                    '1s','3s','10s','30s','100s','300s','1ks','3ks','10ks','30ks']



class Instrument(object):
    def __init__(self,address):
        self.resource = visa.ResourceManager().open_resource(address)

    def query(self, command, *args, **kwargs):
        if args:
            return self.resource.query(command+'? '+args[0]).strip('\r').strip('\n')
        return self.resource.query(command+'?').strip('\r').strip('\n')

    def write(self, command, value):
        return self.resource.write(command+ ' ' +value)

def update_plots(x, R,to_db,y_to_db):
    axarr[0].scatter(x, R)
    axarr[1].scatter(x, to_db)
    axarr[2].scatter(x, y_to_db)
    plt.pause(0.01)


def sweep():

    time_constant = TIME_CONSTANT

    filename = 'EPR_Magnet_AICFU231_PeekShield_Offcentered_September 14 2016 18_09.csv'


    with open(filename, 'rU') as f:
        s = csv.reader(f, delimiter=' ')
        s.next()
        for row in s:
            # print row
            # v = float(row[2].split(',')[3])
            v = float(row[7].split(',')[0])
            x = float(row[1].split(',')[0])
            y = float(row[1].split(',')[1])
            plotly_stream(v,x,y)
            # update_plots(float(v_read),R,to_db,y_to_db)
            time.sleep(0.95*WAIT_TIME)

def plotly_stream(x,y1,y2):
    s_1.write(dict(x=x, y=y1))
    s_2.write(dict(x=x, y=y2))


if __name__ == "__main__":
    s_1.open()
    s_2.open()
    sweep()
    s_1.close()
    s_2.close()
