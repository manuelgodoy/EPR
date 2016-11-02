import visa
import sys, csv, time, datetime, math
import numpy as np
from math import pi
from voltages import voltages
import matplotlib.pyplot as plt


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
    # plt.axis([0.7, 1, 1500, 1750])
    # plt.ion()

    filename = 'Magnet Characterization_'+datetime.datetime.now().strftime("%B %d %Y %H_%M")+'.csv'

    power_supply.write('VOLT:OFFS','0')
    v_read = power_supply.query('VOLT:OFFS')
    power_supply.write('OUTP','ON')
    # c_read = power_supply.query('CURR')

    with open(filename, 'wb') as f:
        s = csv.writer(f, delimiter=' ')
        s.writerow(['Vin,','Field,','Time'])
        start = time.time()
        for i in xrange(100):
            voltage = i*0.001+start_voltage
            power_supply.write('VOLT:OFFS',str(voltage))
            v_read = power_supply.query('VOLT:OFFS')
            g = gauss.query('RDGFIELD')
            update_plots(float(v_read), g)
            end = time.time()
            s.writerow([v_read +',', g+',',end-start])
            time.sleep(0.9)
        power_supply.write('VOLT:OFFS','0.5')
        # power_supply.write('OUTP','OFF')

def update_plots(x, y):
    plt.scatter(x, y)
    # axarr[1].scatter(x, to_db)
    # axarr[2].scatter(x, y_to_db)
    plt.pause(0.05)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        start_voltage = float(sys.argv[1])
    else:
        start_voltage = 0.7
    # lockin = Instrument('GPIB2::8')
    # signal_gen = Instrument('GPIB1::7')
    plt.xlim([0.69, 1])
    plt.ion()
    gauss = Instrument('GPIB2::12')
    power_supply = Instrument('GPIB3::2')
    sweep2(start_voltage)
