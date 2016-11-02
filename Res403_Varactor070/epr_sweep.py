import sys, csv, time, datetime, math
import numpy as np
import pandas as pd
from math import pi, log10
from epr_signal import EPR
from instrument_control import Instrument, sensitivity, time_constants

PLOTLY = True

if PLOTLY:
    from plotly_settings import s_1, s_2, s_3
else:
    import matplotlib.pyplot as plt

NUMBER_OF_POINTS = 50
RESOLUTION = 0.01
VOLTAGE_START = 0.6
TIME_CONSTANT = '300ms'
MODULATION_FREQUENCY = '100000'
WAIT_TIME = 0.3

def update_plots(x, R,to_db,y_to_db):
    axarr[0].scatter(x, R)
    axarr[1].scatter(x, to_db)
    axarr[2].scatter(x, y_to_db)
    plt.pause(0.01)

def plotly_stream(x,y1,y2,y3):
    s_1.write(dict(x=x, y=y1))
    s_2.write(dict(x=x, y=y2))
    s_3.write(dict(x=x, y=y3))

def sweep(start_voltage, sample):
    # Power Supply on before to allow magnet to start
    power_supply.write('VOLT:OFFS',str(VOLTAGE_START))
    power_supply.write('OUTP','ON')

    time_constant = TIME_CONSTANT

    filename = 'EPR_{0}_'.format(sample)+datetime.datetime.now().strftime("%B %d %Y %H:%M:%S")+'.csv'

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
    for i in xrange(NUMBER_OF_POINTS):
        voltage = i*RESOLUTION+start_voltage
        power_supply.write('VOLT:OFFS',str(voltage))
        # data['Voltage Magnet'].append(power_supply.query('VOLT:OFFS'))
        # g = gauss.query('RDGFIELD')
        data['Field'].append('NaN')
        # l = lockin.query('SNAP','1,2,3,4').split(',')
        l = lockin.query('SNAP','1,2,3,4,5').split(',')
        v_read = power_supply.query('VOLT:OFFS')
        sens_index = int(lockin.query('SENS'))
        sens = sensitivity[sens_index]

        X = float(l[0])
        Y = float(l[1])
        R = float(l[2])
        data['X'].append(X)
        data['Y'].append(Y)
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
        plotly_stream(float(v_read),X,Y,R)
        # update_plots(float(v_read),R,X,Y)
        end = time.time()

        data['Sens'].append(sens)
        data['XdB'].append(db)
        data['Voltage Magnet'].append(v_read)
        data['Time'].append(end-start)
        # s.writerow([g +',', l+',',str(db)+',',str(sens)+',',tc+',',res_freq+',',amplitude+',',v_read+',',mod_amplitude+',',mod_frequency+',',end-start])
        # plt.pause(0.05)
        time.sleep(0.95*WAIT_TIME)

    frame = pd.DataFrame(data)
    frame['TC']= pd.Series(tc)
    frame['Resonance Freq'] = dp.Series(res_freq)
    frame['Tx Power'] = pd.Series(amplitude)
    frame['Modulation Amplitude'] = pd.Series(mod_amplitude)
    frame['Modulation Frequency'] = pd.Series(mod_frequency)
    x = EPR(frame['X'])
    y = EPR(frame['Y'])
    r = EPR(frame['R'])
    frame['R pp'] = pd.Series(r.amplitude)
    frame['X pp'] = pd.Series(x.amplitude)
    frame['Y pp'] = pd.Series(y.amplitude)
    frame['Noise'] = pd.Series(r.noise())
    frame['SNR'] = pd.Series(r.amplitude/r.noise())
    frame['SNRdB'] = pd.Series(20*math.log10(frame['SNR'][0]))
    frame['mid point'] = pd.Series(frame['Voltage Magnet'][x.mid_point_index()])

    frame.to_csv(filename, index = False)

    power_supply.write('VOLT:OFFS',str(VOLTAGE_START))
    # power_supply.write('OUTP','OFF')

if __name__ == "__main__":
    if len(sys.argv) > 1:
        start_voltage = VOLTAGE_START
        sample_name = sys.argv[1]
        # coil_type = sys.argv[2]
        try:
            lockin = Instrument('GPIB0::8')
            signal_gen = Instrument('GPIB1::7')
            modulation_gen = Instrument('GPIB3::2')
            power_supply = Instrument('GPIB2::10')
        except Exception as e:
            raise e

        if PLOTLY:
            s_1.open()
            s_2.open()
            s_3.open()
            sweep(start_voltage, sample_name)
            s_1.close()
            s_2.close()
            s_3.close()
        else:
            f, axarr = plt.subplots(3, sharex = True)
            # axarr[0].set_xlim([float(VOLTAGE_START), float(start_voltage)+NUMBER_OF_POINTS*RESOLUTION])
            # axarr[0].grid(which = 'both')
            # axarr[1].set_xlim([float(VOLTAGE_START), float(start_voltage)+NUMBER_OF_POINTS*RESOLUTION])
            # axarr[1].grid(which = 'both')
            # axarr[2].set_xlim([float(VOLTAGE_START), float(start_voltage)+NUMBER_OF_POINTS*RESOLUTION])
            # axarr[2].grid(which = 'both')
            plt.ion()
            sweep(start_voltage, sample_name)
    else:
        print "Enter sample name in modulation coil: 'DPPH' or 'AICFU'"
