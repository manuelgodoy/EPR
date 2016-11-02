import visa
import datetime, csv, sys

# FILENAME = 'S11_'+datetime.datetime.now().strftime("%B %d %Y %H_%M")+'.csv'
START_FREQ = 3.5e9
STOP_FREQ = 5.5e9
CENTER = 4.5e9
SPAN = 2e9

class Instrument(object):
    def __init__(self,address):
        self.resource = visa.ResourceManager().open_resource(address)

    def query(self, command, *args, **kwargs):
        if args:
            return self.resource.query(command+'? '+args[0]).strip('\r').strip('\n')
        return self.resource.query(command+'?').strip('\r').strip('\n')

    def write(self, command, value):
        return self.resource.write(command+ ' ' +value)


def measure_s11(res_type):
    n.write('CALC:PAR:SEL', 'CH1_S11_1')
    p = int(n.query('SENS:SWE:POIN')) #Number of points
    # n.write('INIT:CONT OFF')
    # n.write('INIT:IMM;*wai')
    # d = n.write('CALC:DATA? SDATA')
    n.write('SENS:FREQ:CENT',str(CENTER))
    n.write('SENS:FREQ:SPAN',str(SPAN))
    d = n.query('CALC:DATA','FDATA') #Actual Data
    d_list = d.split(',')
    FILENAME = 'S11_'+res_type+datetime.datetime.now().strftime("%B %d %Y %H_%M")+'.csv'
    with open(FILENAME, 'wb') as f:
        s = csv.writer(f, delimiter=' ')
        s.writerow(['Freq,','s11,'])
        for i in xrange(p):
            freq = CENTER - SPAN/2 + SPAN*i/(p-1)
            s.writerow([str(freq) +',', str(d_list[i])])

def measure_s21(res_type):
    n.write('CALC:PAR:SEL', 'CH1_S21_2')
    p = int(n.query('SENS:SWE:POIN')) #Number of points
    # n.write('INIT:CONT OFF')
    # n.write('INIT:IMM;*wai')
    # d = n.write('CALC:DATA? SDATA')
    n.write('SENS:FREQ:CENT',str(CENTER))
    n.write('SENS:FREQ:SPAN',str(SPAN))
    d = n.query('CALC:DATA','FDATA') #Actual Data
    d_list = d.split(',')
    FILENAME = 'S21_'+res_type+datetime.datetime.now().strftime("%B %d %Y %H_%M")+'.csv'
    with open(FILENAME, 'wb') as f:
        s = csv.writer(f, delimiter=' ')
        s.writerow(['Freq,','s21,'])
        for i in xrange(p):
            freq = CENTER - SPAN/2 + SPAN*i/(p-1)
            s.writerow([str(freq) +',', str(d_list[i])])

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            n = Instrument('GPIB0::16')
        except:
            raise "Problem connecting with device"
        analysis_type = sys.argv[1]
        resonator_type = sys.argv[2]
        if analysis_type == "S11":
            measure_s11(resonator_type)
        elif analysis_type == "S21":
            print "here"
            measure_s21(resonator_type)
    else:
        print "Enter S11 or S21 and Resonator Type"
