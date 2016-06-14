import visa
import sys, csv, time, datetime, math
import numpy as np
from math import pi
import matplotlib.pyplot as plt
from voltages import voltages

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


def sweep(start_voltage):
    time_constant = '3s'
    center = float(lockin.query('OUTP? 1'))
    print center
    g = float(gauss.query('RDGFIELD'))
    # plt.axis([voltages[0], voltages[-1], 0.5*center, 1.5*center])
    plt.axis([float(start_voltage), float(start_voltage)+0.150, -0.001, 0.001])
    plt.ion()

    filename = 'EPR_Magnet'+datetime.datetime.now().strftime("%B %d %Y %H_%M")+'.csv'

    time_constant_index = time_constants.index(time_constant)
    lockin.write('OFLT',str(time_constant_index))
    lockin.write('FREQ','100000')
    res_freq = signal_gen.query('FREQ')
    amplitude = signal_gen.query('POW')
    tc_index = int(lockin.query('OFLT'))
    tc = time_constants[tc_index]
    power_supply.write('VOLT:OFFS','0')
    v_read = power_supply.query('VOLT:OFFS')
    c_read = '0'
    power_supply.write('OUTP','ON')

    with open(filename, 'wb') as f:
        s = csv.writer(f, delimiter=' ')
        s.writerow(['Field,','X,','Y,','R,','Theta,','dB,','Sens,','TC,','ResFreq,','Power,','Vce,','Ic,','Time'])
        start = time.time()
        for i in xrange(100):
            voltage = i*0.001+start_voltage
            power_supply.write('VOLT:OFFS',str(voltage))
            v_read = power_supply.query('VOLT:OFFS')
            g = gauss.query('RDGFIELD')
            l = lockin.query('SNAP','1,2,3,4')
            sens_index = int(lockin.query('SENS'))
            sens = sensitivity[sens_index]
            to_db = float(l.split(',')[0])
            if abs(abs(to_db)-float(sens)) < .25*float(sens):
                lockin.write('SENS',str(sens_index+1))
            elif abs(to_db)/float(sens) < .2:
                lockin.write('SENS',str(sens_index-1))
            try:
                db = 10*math.log10(to_db*to_db/0.050)
            except:
                log.info(to_db)
            plt.scatter(float(v_read), to_db)
            end = time.time()
            s.writerow([g +',', l+',',str(db)+',',sens+',',tc+',',res_freq+',',amplitude+',',v_read+',',c_read+',',end-start])
            # s.writerow([v_read])
            plt.pause(0.05)
            time.sleep(.9)
        power_supply.write('VOLT:OFFS','0')
        power_supply.write('OUTP','OFF')


if __name__ == "__main__":
    if len(sys.argv) > 1:
        start_voltage = float(sys.argv[1])
    else:
        start_voltage = 0.85
    lockin = Instrument('GPIB0::8')
    signal_gen = Instrument('GPIB1::7')
    gauss = Instrument('GPIB3::12')
    power_supply = Instrument('GPIB2::10')
    sweep(start_voltage)
