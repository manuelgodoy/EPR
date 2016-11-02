import ctypes
import numpy as np
import os

class NiUsbTC01(object):
    # type mappings
    int32 = ctypes.c_long
    uInt32 = ctypes.c_ulong
    float64 = ctypes.c_double

    # constants mappings
    tc_types = {
        "J" : 10072,        # DAQmx_Val_J_Type_TC
        "K" : 10073,        # DAQmx_Val_K_Type_TC
        "N" : 10077,        # DAQmx_Val_N_Type_TC
        "R" : 10082,        # DAQmx_Val_R_Type_TC
        "S" : 10085,        # DAQmx_Val_S_Type_TC
        "T" : 10086,        # DAQmx_Val_T_Type_TC
        "B" : 10047 ,       # DAQmx_Val_B_Type_TC
        "E" : 10055,        # DAQmx_Val_E_Type_TC
    }

    temp_units = {
        "C" : 10143,        # DAQmx_Val_DegC
        "F" : 10144,        # DAQmx_Val_DegF
        "K" : 10325,        # DAQmx_Val_Kelvins
    }

    def __init__(self, device_id="Dev1", channel_id="ai0", tc_type="K", temp_unit="C", temp_min=-50, temp_max=100):
        # load the DLL
        nidaq_dll_path = os.path.join(os.path.dirname(os.path.realpath("__file__")), "bin/nicaiu.dll")
        self.nidaq = ctypes.WinDLL(nidaq_dll_path)

        # alternatively, if runtime is installed & registered:
        # self.nidaq = ctypes.windll.nicaiu

        self.task_handle = self.uInt32(0)
        physical_channel = "{}/{}".format(device_id, channel_id)

        # reset device
        self.nidaq.DAQmxResetDevice(device_id.encode("ASCII"))

        # create task
        self._nidaq_assert(self.nidaq.DAQmxCreateTask(b"", ctypes.byref(self.task_handle)))

        # create channel
        self._nidaq_assert(self.nidaq.DAQmxCreateAIThrmcplChan(
            self.task_handle,
            physical_channel.encode("ASCII"),
            b"",
            self.float64(temp_min),
            self.float64(temp_max),
            self.temp_units[temp_unit],
            self.tc_types[tc_type],
            10200,             # DAQmx_Val_BuiltIn   //  CJC Source "Built-In"
            self.float64(0),
            b""
        ))

        # start task
        self._nidaq_assert(self.nidaq.DAQmxStartTask(self.task_handle))

    def __del__(self):
        try:
            self._close_task()
        except:
            pass  # worth a try

    def _close_task(self):
        if self.task_handle.value != 0:
            self.nidaq.DAQmxStopTask(self.task_handle)
            self.nidaq.DAQmxClearTask(self.task_handle)

    def _nidaq_assert(self, err):
        """Raise Exception if return code 'err' is not 0."""
        if not err == 0:
            buf_size = 300
            buf = ctypes.create_string_buffer(b'\0' * buf_size)
            self.nidaq.DAQmxGetErrorString(err, ctypes.byref(buf), buf_size)
            raise Exception('nidaq call failed with error {}: {}'.format(err, repr(buf.value)))

    def get_temperature(self):
        read = self.int32()
        data = np.zeros(1, dtype=np.float64)  # size 1 array, passed by ref to be filled

        self._nidaq_assert(self.nidaq.DAQmxReadAnalogF64(
            self.task_handle,
            1,                          # number samples per channel
            self.float64(1.0),          # timeout in sec
            0,                          # DAQmx_Val_GroupByChannel   // Group by Channel
            data.ctypes.data,           # the array byref
            1,                          # array size in samples
            ctypes.byref(read),         # samples per channel read (return value)
            None                        # reserved
        ))

        return data[0]

if __name__ == "__main__":
    sensor = NiUsbTC01()
    print(sensor.get_temperature())
