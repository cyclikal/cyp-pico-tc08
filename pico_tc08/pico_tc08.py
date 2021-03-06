import ctypes
import json

from cyckei.plugins import cyp_base
from picosdk.usbtc08 import usbtc08
from picosdk.errors import PicoSDKCtypesError

# Configuration should be loaded from a file, optionally, in the future
# Set default hermocouple type, must be consistent
thermocouple_type = "K"
# Different thermocouple types need to be specified when reading
thermocouple_type_map = {
    "B": 66, "E": 69, "J": 74, "K": 75, "N": 78,
    "R": 82, "S": 83, "T": 84, " ": 32, "X": 88,
}

default_config = json.loads(
    """
    {
        "name": "pico_tc08",
        "enabled": true,
        "sources": [
            {
              "port": 1,
              "meta": ["K", "K", "K", "K", "K", "K", "K", "K"]
            }
        ]
    }
    """
)


def check_api_response(response):
    """
    Function tests to a usbtc08 wrapper functions output for errors.
    It returns the existing response if successful, and raises a
    PicoSDKCtypesError including the last_error if the function fails.
    """
    if type(response) is not int:
        raise TypeError
    elif response < 1:
        error = usbtc08.usb_tc08_get_last_error(response)
        raise PicoSDKCtypesError("Unsuccessful API call:", error)
    else:
        return response


def autonomous_read_all():
    controller = PluginController()
    results = cyp_base.read_all(controller)
    controller.cleanup()

    return results


class PluginController(cyp_base.BaseController):
    def __init__(self, sources):
        # Run default parent tasks
        super().__init__(
            "pico-tc08",
            "Gets temperature data from Pico-TC08 thermocouples."
        )

        # Initialize TC-08 Devices, by iteratating until none left.
        self.devices = self.load_devices(sources)
        self.logger.info(f"Connected {len(self.devices)} Pico TC-08(s)")

        # Create a PicoChannel object for each Device
        self.sources = self.load_sources()

        # List of names to declare to Cyckei
        self.names = []
        for source in self.sources:
            self.names.append(str(source))

    def load_devices(self, sources):
        devices = []
        handler = ctypes.c_int16()

        # Get list if ports
        device_ports = []
        for source in sources:
            device_ports.append(source["port"])
        device_ports.sort()

        for device in sources:
            # Using ctypes Handler like PicoSDK Example
            response = usbtc08.usb_tc08_open_unit()
            if response == 0:
                # Returns zero when no unopened units left
                break
            if response not in device_ports:
                check_api_response(usbtc08.usb_tc08_close_unit(handler))
                break
            else:
                # Check if opened sucessfully, and assign handler
                handler = check_api_response(response)
                # Set each device to reject either 50 or 60 Hz interference
                # 1: Reject 60Hz, 2: Reject 50Hz
                check_api_response(usbtc08.usb_tc08_set_mains(handler, 0))
            devices.append(handler)

        return devices

    def load_sources(self):
        sources = {}

        for handler in self.devices:
            # Create a PicoChannel object for each channel
            for channel in range(1, 9):
                if channel == 0:
                    # In case this iterates over a cold junction in the future
                    name = f"Temp {handler}-CJ"
                else:
                    name = f"Temp {handler}-{channel}"
                sources[name] = PluginSource(handler, channel,
                                             thermocouple_type, name)

        return sources

    def cleanup(self):
        # Closes all devices
        for handler in self.devices:
            check_api_response(usbtc08.usb_tc08_close_unit(handler))
        self.logger.info("Closed all devices.")


class PluginSource(cyp_base.BaseSource):
    def __init__(self, handler, channel, type, name):
        super().__init__()
        self.name = name
        self.channel = channel
        # Again, should check timing using ctypes
        self.type = ctypes.c_int8(thermocouple_type_map[type])
        self.device = handler

        # Setup individual channel for reading, with couple type
        check_api_response(
            usbtc08.usb_tc08_set_channel(
                self.device, self.channel, self.type))

    def read(self):
        # Read instantaneous temperature
        temp = (ctypes.c_float * 9)()
        overflow = ctypes.c_int16(0)
        # USBTC08_UNITS_CENTIGRADE, USBTC08_UNITS_FAHRENHEIT,
        # USBTC08_UNITS_KELVIN, USBTC08_UNITS_RANKINE
        units = usbtc08.USBTC08_UNITS["USBTC08_UNITS_CENTIGRADE"]
        check_api_response(usbtc08.usb_tc08_get_single(
               self.device, ctypes.byref(temp),
               ctypes.byref(overflow), units))

        return temp[self.channel]


if __name__ == "__main__":
    sources = default_config["sources"]
    controller = PluginController(sources)
    print(cyp_base.read_all(controller))
