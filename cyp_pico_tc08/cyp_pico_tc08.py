import logging
import ctypes

from cyckei.plugins import cyp_base
from picosdk.usbtc08 import usbtc08
from picosdk.errors import PicoSDKCtypesError

logger = logging.getLogger("cyckei")

# Configuration should be loaded from a file, optionally.
# Set default hermocouple type, must be consistent.
thermocouple_type = "K"
# Different thermocouple types need to be specified when reading
thermocouple_type_map = {
    "B": 66, "E": 69, "J": 74, "K": 75, "N": 78,
    "R": 82, "S": 83, "T": 84, " ": 32, "X": 88,
}


def assert_api_response(response):
    """
    Function tests to a usbtc08 wrapper functions output for errors.
    It returns the existing response if successful, and raises a
    PicoSDKCtypesError including the last_error if the function fails.
    """
    if response > 0:
        return response
    else:
        error = usbtc08.usb_tc08_get_last_error(response)
        raise PicoSDKCtypesError(f"Unsuccessful API call: {error}")
        return 0


class PicoController(cyp_base.PluginController):
    def __init__(self):
        # Run default parent tasks
        super().__init__()

        # Initialize TC-08 Devices, by iteratating until none left.
        self.device_handles = []
        while True:
            # Using ctypes handle like PicoSDK Example
            # Should test for speed improvements
            handle = ctypes.c_int16()
            response = usbtc08.usb_tc08_open_unit()
            if response == 0:
                break
            else:
                handle = assert_api_response(response)
                self.device_handles.append(handle)

        logger.debug(f"Connected {len(self.device_handles)} Pico TC-08s")

        # Create a PicoChannel object for each Device
        self.sources = {}
        for handle in self.device_handles:
            # Set each device to reject either 50 or 60 Hz interference
            # 1: Reject 60Hz, 2: Reject 50Hz
            assert_api_response(usbtc08.usb_tc08_set_mains(handle, 0))

            # Create a PicoChannel object for each channel
            for channel in range(1, 9):
                if channel == 0:
                    # In case this iterates of a thermocouple in the future
                    name = f"Temp {handle}-CJ"
                else:
                    name = f"Temp {handle}-{channel}"
                self.sources[name] = PicoChannel(handle, channel,
                                                 thermocouple_type, name)

            # Check minimum sampling interval
            interval = assert_api_response(
                usbtc08.usb_tc08_get_minimum_interval_ms(handle))

            # Start polling all device channels that were setup
            interval = assert_api_response(
                usbtc08.usb_tc08_run(handle, interval))

            logger.debug(
                f"Started device {handle} with {interval}ms minimum interval")

    def cleanup(self):
        # Closes all devices
        for handle in self.device_handles:
            assert_api_response(usbtc08.usb_tc08_close_unit(handle))
        logger.debug("Closed all devices.")


class PicoChannel(cyp_base.SourceObject):
    def __init__(self, handle, channel, type, name):
        super().__init__()
        self.name = name
        self.channel = channel
        # Again, should check timing using ctypes
        self.type = ctypes.c_int8(thermocouple_type_map[type])
        self.device = handle

        # Setup individual channel for reading, with couple type
        assert_api_response(
            usbtc08.usb_tc08_set_channel(
                self.device, self.channel, self.type))

    def read(self):
        # Read instantaneous temperature

        temp = (ctypes.c_float * 2 * 15)()
        temp_times = (ctypes.c_int32 * 15)()
        overflow = ctypes.c_int16()
        # USBTC08_UNITS_CENTIGRADE, USBTC08_UNITS_FAHRENHEIT,
        # USBTC08_UNITS_KELVIN, USBTC08_UNITS_RANKINE
        units = usbtc08.USBTC08_UNITS["USBTC08_UNITS_CENTIGRADE"]
        reading = usbtc08.usb_tc08_get_temp(
            self.device,
            ctypes.byref(temp),
            ctypes.byref(temp_times),
            15,
            ctypes.byref(overflow),
            self.channel,
            units,
            1)
        if reading == -1:
            reading = assert_api_response(reading)

        return temp


if __name__ == "__main__":
    # Select channel to read on direct run, 0 for all
    channel = 1
    controller = PicoController()

    if channel == 0:
        reading = cyp_base.read_all(controller)
    else:
        reading = controller.read(f"Temp 1-{channel}")

    for i in reading:
        for j in i:
            print(f"{j}, ", end="")
        print()

    controller.cleanup()
