import visa
import sys, csv, time, datetime, math
import numpy as np
import pandas as pd
from math import pi, log10
import matplotlib.pyplot as plt
# from voltages import voltages

from plotly_settings import s_1, s_2
import epr_amplitude

NUMBER_OF_POINTS = 40
RESOLUTION = 0.0005
VOLTAGE_START = 0.705
TIME_CONSTANT = '300ms'
MODULATION_FREQUENCY = '100000'
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


def sweep(start_voltage, sample, coil):
    # Power Supply on before to allow magnet to start
    power_supply.write('VOLT:OFFS',str(VOLTAGE_START))
    power_supply.write('OUTP','ON')

    time_constant = TIME_CONSTANT

    filename = 'EPR_Magnet_{0}_{1}_'.format(sample, coil)+datetime.datetime.now().strftime("%B %d %Y %H:%M:%S")+'.csv'

    time_constant_index = time_constants.index(time_constant)
    lockin.write('OFLT',str(time_constant_index))
    lockin.write('FREQ','100000')
    res_freq = signal_gen.query('FREQ')
    amplitude = signal_gen.query('POW')
    tc_index = int(lockin.query('OFLT'))
    tc = time_constants[tc_index]
    mod_amplitude = modulation_gen.query('VOLT')
    mod_frequency = modulation_gen.query('FREQ')

    headers = ['Field','X','Y','R','Rdb','Theta','XdB','Sens','TC',\
    'Resonance Freq','Tx Power','Voltage Magnet','Modulation Amplitude',\
    'Modulation Frequency','Time']
    data = {key: [] for key in headers}
    start = time.time()
    # s = csv.writer(f, delimiter=' ')
    # s.writerow(['Field,','X,','Y,','R,','Rdb,','Theta,','dB,','Sens,','TC,','ResFreq,','Power,','VMagnet,','ModAmplitude,','ModFrequency,','Time'])
    for i in xrange(NUMBER_OF_POINTS):
        voltage = i*RESOLUTION+start_voltage
        power_supply.write('VOLT:OFFS',str(voltage))
        # data['Voltage Magnet'].append(power_supply.query('VOLT:OFFS'))
        # g = gauss.query('RDGFIELD')
        data['Field'].append('na')
        # l = lockin.query('SNAP','1,2,3,4').split(',')
        l = lockin.query('SNAP','1,2,3,4,5').split(',')
        v_read = power_supply.query('VOLT:OFFS')

        sens_index = int(lockin.query('SENS'))
        sens = sensitivity[sens_index]

        X = float(l[0])
        Y = float(l[1])
        data['X'].append(X)
        data['Y'].append(Y)
        R = float(l[2])
        data['R'].append(R)
        # RdB = 0
        RdB = float(l[3])
        data['Rdb'].append(RdB)
        data['Theta'].append(l[3])

        # if abs(abs(R)-float(sens)) < .25*float(sens):
        #     lockin.write('SENS',str(sens_index+1))
        # elif abs(R)/float(sens) < .2: #and abs(y)/float(sens) < .2:
        #     lockin.write('SENS',str(sens_index-1))

        if abs(RdB)-abs(sens) > 11:
           lockin.write('SENS',str(sens_index-1))
        elif abs(RdB)-abs(sens) < 1:
           lockin.write('SENS',str(sens_index+1))

        try:
            db = 10*math.log10(X*X/0.050)
            # data['XdB'].append(db)
            # Rdb = 10*math.log10(Rto_db*Rto_db/0.050)
        except:
            # log.info(to_db)
            print (X)
        plotly_stream(float(v_read),X,Y)
        # update_plots(float(v_read),R,X,Y)
        end = time.time()

        data['Sens'].append(sens)
        data['XdB'].append(db)
        data['Voltage Magnet'].append(v_read)
        data['Time'].append(end-start)
        # s.writerow([g +',', l+',',str(db)+',',str(sens)+',',tc+',',res_freq+',',amplitude+',',v_read+',',mod_amplitude+',',mod_frequency+',',end-start])
        # plt.pause(0.05)
        time.sleep(0.95*WAIT_TIME)

        data['TC'].append(tc)
        data['Resonance Freq'].append(res_freq)
        data['Tx Power'].append(amplitude)
        data['Modulation Amplitude'].append(mod_amplitude)
        data['Modulation Frequency'].append(mod_frequency)

    frame = pd.DataFrame(data)
    frame['R pp'] = epr_amplitude.amplitude(np.array(frame['R']))
    frame['X pp'] = epr_amplitude.amplitude(np.array(frame['X']))
    frame['Y pp'] = epr_amplitude.amplitude(np.array(frame['Y']))
    frame['Noise'] = frame['R'].tail(5).std()
    frame['SNR'] = frame['R pp'][0]/frame['Noise'][0]
    frame['SNRdB'] = 20*math.log10(frame['SNR'][0])
    frame['mid point'] = frame['Voltage Magnet'][epr_amplitude.mid_point_index(np.array(frame['R']))]

    frame.to_csv(filename, index = False)

    power_supply.write('VOLT:OFFS',str(VOLTAGE_START))
    # power_supply.write('OUTP','OFF')

def plotly_stream(x,y1,y2):
    s_1.write(dict(x=x, y=y1))
    s_2.write(dict(x=x, y=y2))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        start_voltage = VOLTAGE_START
        sample_name = sys.argv[1]
        coil_type = sys.argv[2]
        try:
            lockin = Instrument('GPIB0::8')
            signal_gen = Instrument('GPIB1::7')
            modulation_gen = Instrument('GPIB3::2')
            power_supply = Instrument('GPIB2::10')
        except Exception as e:
            raise e
        # f, axarr = plt.subplots(3, sharex = True)
        # axarr[0].set_xlim([float(VOLTAGE_START), float(start_voltage)+NUMBER_OF_POINTS*RESOLUTION])
        # axarr[0].grid(which = 'both')
        # axarr[1].set_xlim([float(VOLTAGE_START), float(start_voltage)+NUMBER_OF_POINTS*RESOLUTION])
        # axarr[1].grid(which = 'both')
        # axarr[2].set_xlim([float(VOLTAGE_START), float(start_voltage)+NUMBER_OF_POINTS*RESOLUTION])
        # axarr[2].grid(which = 'both')
        # plt.ion()

        s_1.open()
        s_2.open()
        sweep(start_voltage, sample_name, coil_type)
        s_1.close()
        s_2.close()

    else:
        print "Enter sample name and voltage level in modulation coil: 'DPPH 10Vpp' or 'AICFU CurrAmp'"
