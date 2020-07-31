import logging
import ctypes

from cyckei.plugins import cyp_base
from picosdk.usbtc08 import usbtc08

logger = logging.getLogger("cyckei")


class PicoController(cyp_base.PluginController):
    def __init__(self):
        self.c_handler = ctypes.c_int16()

        # Initialize TC-08 Device
        print("Open", usbtc08.usb_tc08_open_unit())
        print("Set", usbtc08.usb_tc08_set_mains(self.c_handler, 0))

        # Run default parent tasks, including get_sources
        super().__init__()

    def get_sources(self):
        """
        Searches for available sources, and establishes source objects.

        Returns
        -------
        Dictionary of sources in format "name": SourceObject.
        """

        # Find Connected Sources
        thermocouple_type = {
            "B": 66, "E": 69, "J": 74, "K": 75, "N": 78,
            "R": 82, "S": 83, "T": 84, "?": 32, "X": 88,
        }

        sources = {}
        sources["Temp1"] = PicoChannel(1, thermocouple_type["K"],
                                       self.c_handler)
        sources["Temp2"] = PicoChannel(2, thermocouple_type["K"],
                                       self.c_handler)

        return sources

    def cleanup(self):
        # Closes device
        print("Close", usbtc08.usb_tc08_close_unit(self.c_handler))


class PicoChannel(cyp_base.SourceObject):
    def __init__(self, port, type, c_handler):
        super().__init__()
        self.range = [0, port]
        self.name = f"Random 0-{port}"
        self.port = port
        self.type = ctypes.c_int8(type)
        self.c_handler = c_handler

    def read(self):
        # Setup individual channel for reading, with couple type
        print("Assign", usbtc08.usb_tc08_set_channel(self.c_handler, self.port,
                                                     self.type))
        print("Min", usbtc08.usb_tc08_get_minimum_interval_ms(self.c_handler))

        # Read temperature
        temp = (ctypes.c_float * 9)()
        overflow = ctypes.c_int16(0)
        units = usbtc08.USBTC08_UNITS["USBTC08_UNITS_CENTIGRADE"]
        print("Get", usbtc08.usb_tc08_get_single(
              self.c_handler, ctypes.byref(temp),
              ctypes.byref(overflow), units))

        print(temp)


if __name__ == "__main__":
    controller = PicoController()
    print("Read", cyp_base.read_all(controller))
    controller.cleanup()
