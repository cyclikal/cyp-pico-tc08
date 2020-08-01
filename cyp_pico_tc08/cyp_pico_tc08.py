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
        self.device_handlers = []
        while True:
            # Using ctypes Handler like PicoSDK Example
            # Should test for speed improvements
            handler = ctypes.c_int16()
            response = usbtc08.usb_tc08_open_unit()
            if response == 0:
                break
            else:
                handler = assert_api_response(response)
                self.device_handlers.append(handler)

        logger.debug(f"Connected {len(self.device_handlers)} Pico TC-08s")

        # Create a PicoChannel object for each Device
        self.sources = {}
        for handler in self.device_handlers:
            # Set each device to reject either 50 or 60 Hz interference
            # 1: Reject 60Hz, 2: Reject 50Hz
            assert_api_response(usbtc08.usb_tc08_set_mains(handler, 0))

            # Create a PicoChannel object for each channel
            for channel in range(1, 9):
                if channel == 0:
                    # In case this iterates of a thermocouple in the future
                    name = f"Temp {handler}-CJ"
                else:
                    name = f"Temp {handler}-{channel}"
                self.sources[name] = PicoChannel(handler, channel,
                                                 thermocouple_type, name)

            # Check minimum sampling interval
            interval = assert_api_response(
                usbtc08.usb_tc08_get_minimum_interval_ms(handler))

            logger.debug(
                f"Started device {handler} with {interval}ms minimum interval")

    def cleanup(self):
        # Closes all devices
        for handler in self.device_handlers:
            assert_api_response(usbtc08.usb_tc08_close_unit(handler))
        logger.debug("Closed all devices.")


class PicoChannel(cyp_base.SourceObject):
    def __init__(self, handler, channel, type, name):
        super().__init__()
        self.name = name
        self.channel = channel
        # Again, should check timing using ctypes
        self.type = ctypes.c_int8(thermocouple_type_map[type])
        self.device = handler

        # Setup individual channel for reading, with couple type
        assert_api_response(
            usbtc08.usb_tc08_set_channel(
                self.device, self.channel, self.type))

    def read(self):
        # Read instantaneous temperature
        temp = (ctypes.c_float * 9)()
        overflow = ctypes.c_int16(0)
        # USBTC08_UNITS_CENTIGRADE, USBTC08_UNITS_FAHRENHEIT,
        # USBTC08_UNITS_KELVIN, USBTC08_UNITS_RANKINE
        units = usbtc08.USBTC08_UNITS["USBTC08_UNITS_CENTIGRADE"]
        assert_api_response(usbtc08.usb_tc08_get_single(
               self.device, ctypes.byref(temp),
               ctypes.byref(overflow), units))

        return temp[self.channel]


if __name__ == "__main__":
    controller = PicoController()

    results = cyp_base.read_all(controller)

    for temp in results:
        print(temp)

    controller.cleanup()
