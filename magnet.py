import visa
import sys, csv, time, datetime, math
import numpy as np
from math import pi
from voltages import voltages
import matplotlib.pyplot as plt

sensitivity = ['2e-9','5e-9','10e-9','20e-9','50e-9','100e-9','200e-9','500e-9','1e-6',
                '2e-6','5e-6','10e-6','20e-6','50e-6','100e-6','200e-6','500e-6','1e-3',
                '2e-3','5e-3','10e-3','20e-3','50e-3','100e-3','200e-3','500e-3','1']
time_constants = ['10us','30us','100us','300us','1ms','3ms','10ms','30ms','100ms','300ms',
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


def sweep(time_constant):
    plt.axis([0.8, 1, 1550, 1750])
    plt.ion()

    filename = 'Magnet Characterization_'+datetime.datetime.now().strftime("%B %d %Y %H_%M")+'.csv'



    power_supply.write('VOLT:OFFS','0')
    v_read = power_supply.query('VOLT:OFFS')
    power_supply.write('OUTP','ON')
    # c_read = power_supply.query('CURR')
    c_read = '0.0'
    with open(filename, 'wb') as f:
        s = csv.writer(f, delimiter=' ')
        s.writerow(['Vin,','Field,','Time'])
        start = time.time()
        for i in voltages:
            voltage = i
            power_supply.write('VOLT:OFFS',str(voltage))
            v_read = power_supply.query('VOLT:OFFS')
            g = gauss.query('RDGFIELD')
            plt.scatter(float(v_read), g)
            end = time.time()
            s.writerow([v_read +',', g+',',end-start])
            plt.pause(0.05)
            time.sleep(1.4)
        power_supply.write('VOLT:OFFS','0')

def sweep2(start_voltage):
    plt.axis([0.7, 1, 1500, 1750])
    plt.ion()

    filename = 'Magnet Characterization_'+datetime.datetime.now().strftime("%B %d %Y %H_%M")+'.csv'

    power_supply.write('VOLT:OFFS','0')
    v_read = power_supply.query('VOLT:OFFS')
    power_supply.write('OUTP','ON')
    # c_read = power_supply.query('CURR')

    with open(filename, 'wb') as f:
        s = csv.writer(f, delimiter=' ')
        s.writerow(['Vin,','Field,','Time'])
        start = time.time()
        for i in xrange(200):
            voltage = i*0.001+start_voltage
            power_supply.write('VOLT:OFFS',str(voltage))
            v_read = power_supply.query('VOLT:OFFS')
            g = gauss.query('RDGFIELD')
            plt.scatter(float(v_read), g)
            end = time.time()
            s.writerow([v_read +',', g+',',end-start])
            plt.pause(0.05)
            time.sleep(0.9)
        power_supply.write('VOLT:OFFS','0.5')
        # power_supply.write('OUTP','OFF')

if __name__ == "__main__":
    if len(sys.argv) > 1:
        start_voltage = float(sys.argv[1])
    else:
        start_voltage = 0.7
    # lockin = Instrument('GPIB2::8')
    # signal_gen = Instrument('GPIB1::7')
    gauss = Instrument('GPIB3::12')
    power_supply = Instrument('GPIB2::10')
    sweep2(start_voltage)
