from pyftdi.ftdi import Ftdi
from struct import pack
import time

VENDOR = 0x0403
PRODUCT = 0x6001
SYNC = [0x55,0xAA]
FACTOR = 2**16/2.5

class Controller(Ftdi):
    def __init__(self):
        super(Controller, self).__init__()
        self.baudrate = 115200

    def open(self, vendor = VENDOR, product = PRODUCT, interface = 1):
        return super(Controller, self).open(vendor = vendor, product = product, interface = interface)

    def write_data(self, command, *data):
        """mofidied method of write_data:
        command: SW list of commands in byte (from 01 to 19 in hex form)
        data: data to be written in byte"""
        size = self._convert_to_list(pack('H',len(data)))
        if not data:
            d = []
            checksum = [0x00,0x00]
        else:
            d = [i for i in data]
            checksum = self._checksum(*data)
        message = SYNC + [command] + [0x00] + size + d + checksum
        return super(Controller, self).write_data(message)

    def read_data(self):
        data = super(Controller, self).read_data(100)
        return self._convert_to_list(data)

    def write_data_v2(self, command, *data):
        """mofidied method of write_data:
        command: SW list of commands in byte (from 01 to 19 in hex form)
        data: data to be written in byte
        returns data received from uC"""
        self.write_data(command, *data)
        time.sleep(0.5)
        data = self.read_data()[6:] #the first 6 bytes are not important
        return data

    def _checksum(self, *data):
        if data:
            return self._convert_to_list(pack('H',sum(data)))
        return

    def _convert_to_list(self, data):
        return [ord(i) for i in data]

def _convert_to_list(data):
    return [ord(i) for i in data]

def set_vreg_v(oneptwo_adj_1):
    pass
    #TODO

def en_vreg(enablers = 0xffff):
    return _convert_to_list(pack('H',enablers))

def read_vreg_v(word):
    LENGTH = 24
    import numpy as np
    word_array = np.array(word[:LENGTH])
    den_array = np.array([20.0,10.0,200.0,200.0,100.0,100.0,100.0,100.0,100.0,\
        100.0,100.0,100.0,100.0,100.0,100.0,50.0,50.0,50.0,50.0,10.0,1.0,\
        1.0,1000.0,1000.0])
    new_word = word_array/den_array
    return(list(new_word))

def read_vreg_i(word):
    LENGTH = 26
    import numpy as np
    word_array = np.array(word[:LENGTH])
    den_array = np.array([100.0,1000.0,1000.0,1000.0,1000.0,1000.0,1000.0,100.0,100.0,\
        1000.0,500.0,1000.0,1000.0,1000.0,500.0,1000.0,1000.0,1000.0,1000.0,200.0,500.0,\
        1.0,100.0,100.0,100.0,1.0])
    new_word = word_array/den_array
    return(list(new_word))

def set_freq(freq):
    b = pack('i',freq)
    b_list = _convert_to_list(b)
    data = b_list[2:] + b_list[:2]
    return data

def en_pll(enable = 0xff):
    return [enable, 0x00]

def read_epr(word):
    import numpy as np
    word_array = np.array(word)
    #TODO


def set_modamp(amp = 5,mod_freq = 100):
    data = [mod_freq, amp*10]
    return data

def en_modamp(enable = 0xff):
    data = [enable, 0x00]
    return data

def set_magnet_control(start,stop,v_step,t_step):
    """t_step in 100ms"""
    data = _convert_to_list(pack('H',start*FACTOR)) + \
            _convert_to_list( pack('H',stop*FACTOR)) + \
            _convert_to_list( pack('H',v_step*FACTOR)) + \
            _convert_to_list( pack('H',t_step))
    return data

def init_pll_hmc837():
    return

def read_vref(word):
    LENGTH = 2
    vref = (word[0]+(word[1]<<8))/10000.
    return vref

def set_magnet_value(volt):
    return _convert_to_list(pack('H',volt*FACTOR))

def set_varactor(volt):
    return _convert_to_list(pack('H',volt*1000))

def read_progress(word):
    iteration = word[0] + (word[1]<<8)
    vref = (word[4] + (word[5]<<8)) / 10000.
    percentage = (word[2] + (word[3] << 8) ) / 100.
    v_var = word[6] + (word[7] << 8)
    freq = word[8] + (word[9] << 8) + (word[10] << 16) + (word[11] << 24)
    done = word[12] + (word[13] << 8)
    return [iteration, vref, percentage, v_var, freq, done]

# def force_varactor(volt):
#     _convert_to_list(pack('H'),volt)

def sweep_freq(span, step):
    data = _convert_to_list(pack('i', span * 2**16)) + _convert_to_list(pack('i', step * 2**16))
    return data

def sweep_varactor(span, step):
    data = _convert_to_list(pack('i', span * 1000)) + _convert_to_list(pack('i', step * 1000))
    return data

def set_sweep_time(time):
    data = _convert_to_list(pack('H', time))
    return data
