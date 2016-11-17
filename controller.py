from pyftdi.ftdi import Ftdi
# from pylibftdi import Device
from struct import pack

VENDOR = 0x0403
PRODUCT = 0x6001
SYNC = [0x55,0xAA]
READ_V = [0x0F,0x00,0x00,0x00]

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
        # if not data:
        d = [0x00, 0x00]
        checksum = [0x00,0x00]
        if data:
            d = [i for i in data]
            checksum = self._checksum(data)
        return super(Controller, self).write_data(SYNC + [command] + [0x00] + d + checksum)

    def read_data(self):
        data = super(Controller, self).read_data(30)
        return self._convert_to_list(data)

    def _checksum(self, *data):
        if data:
            return self._convert_to_list(pack('H',sum(data)))
        return

    def _convert_to_list(self, data):
        return [ord(i) for i in data]
