import visa
import sys, csv, time, datetime, math
import numpy as np
from math import pi
import matplotlib.pyplot as plt
from voltages import voltages

NUMBER_OF_POINTS = 200
RESOLUTION = 0.001
VOLTAGE_START = 0.65
TIME_CONSTANT = '1s'
MODULATION_FREQUENCY = '100'
WAIT_TIME = 1

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
    time_constant = TIME_CONSTANT
    center_to_db = float(lockin.query('OUTP? 3'))
    center = 10*math.log10(center_to_db*center_to_db/0.050)
    g = float(gauss.query('RDGFIELD'))
    # plt.axis([voltages[0], voltages[-1], 0.5*center, 1.5*center])
    plt.axis([float(start_voltage), float(start_voltage)+NUMBER_OF_POINTS*RESOLUTION, center - 20, center + 40])
    plt.grid(which = 'both')
    plt.ion()

    filename = 'Magnet_Test_100Hz_Oil_'+datetime.datetime.now().strftime("%B %d %Y %H_%M")+'.csv'

    time_constant_index = time_constants.index(time_constant)
    lockin.write('OFLT',str(time_constant_index))
    lockin.write('FREQ',MODULATION_FREQUENCY)
    res_freq = signal_gen.query('FREQ')
    amplitude = signal_gen.query('POW')
    tc_index = int(lockin.query('OFLT'))
    tc = time_constants[tc_index]
    power_supply.write('VOLT:OFFS','0')
    power_supply.write('APPL:SIN',MODULATION_FREQUENCY+', 0.04, 0')
    v_read = power_supply.query('VOLT:OFFS')
    c_read = '0'
    power_supply.write('OUTP','ON')

    with open(filename, 'wb') as f:
        s = csv.writer(f, delimiter=' ')
        s.writerow(['Field,','X,','Y,','R,','Theta,','dB,','RdB,','Sens,','TC,','ResFreq,','Power,','Vce,','Ic,','Time'])
        start = time.time()
        for i in xrange(NUMBER_OF_POINTS):
            voltage = i*RESOLUTION+start_voltage
            # power_supply.write('VOLT:OFFS',str(voltage))
            power_supply.write('APPL:SIN',MODULATION_FREQUENCY+', 0.04, '+str(voltage))
            v_read = power_supply.query('VOLT:OFFS')
            g = gauss.query('RDGFIELD')
            l = lockin.query('SNAP','1,2,3,4')
            sens_index = int(lockin.query('SENS'))
            sens = sensitivity[sens_index]
            to_db = float(l.split(',')[0])
            Rto_db = float(l.split(',')[2])
            # y = float(l.split(',')[1])
            if abs(abs(Rto_db)-float(sens)) < .25*float(sens): #or abs(abs(y)-float(sens)) < .25*float(sens):
                lockin.write('SENS',str(sens_index+1))
            elif abs(Rto_db)/float(sens) < .2: #and abs(y)/float(sens) < .2:
                lockin.write('SENS',str(sens_index-1))
            try:
                db = 10*math.log10(to_db*to_db/0.050)
                Rdb = 10*math.log10(Rto_db*Rto_db/0.050)
            except:
                # log.info(to_db)
                print to_db
            plt.scatter(float(v_read), Rdb)
            end = time.time()
            s.writerow([g +',', l+',',str(db)+',',str(Rdb)+',',sens+',',tc+',',res_freq+',',amplitude+',',v_read+',',c_read+',',end-start])
            # s.writerow([v_read])
            plt.pause(0.05)
            time.sleep(0.95*WAIT_TIME)
        power_supply.write('VOLT:OFFS',str(VOLTAGE_START))
        # power_supply.write('OUTP','OFF')


if __name__ == "__main__":
    if len(sys.argv) > 1:
        start_voltage = float(sys.argv[1])
    else:
        start_voltage = VOLTAGE_START
    lockin = Instrument('GPIB0::8')
    signal_gen = Instrument('GPIB1::7')
    gauss = Instrument('GPIB3::12')
    power_supply = Instrument('GPIB2::10')
    sweep(start_voltage)
