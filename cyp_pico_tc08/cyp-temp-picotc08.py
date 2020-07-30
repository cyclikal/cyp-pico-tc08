import logging
from os.path import basename, join
import json

logger = logging.getLogger('cyckei')

DEFAULT_CONFIG = {
    "name":  basename(__file__)[:-3],
    "version": "0.1.dev1",
    "description": "Collects temperature",
    "requirements": ["PicoSDK C Libraries"],
    "sources": [
        {
            "readable": "Thermocouple 1",
            "port": "1",
        },
        {
            "readable": "Thermocouple 2",
            "port": "2",
        },
        {
            "readable": "Thermocouple 3",
            "port": "3",
        },
        {
            "readable": "Thermocouple 4",
            "port": "4",
        },
        {
            "readable": "Thermocouple 5",
            "port": "5",
        },
        {
            "readable": "Thermocouple 6",
            "port": "6",
        },
        {
            "readable": "Thermocouple 7",
            "port": "7",
        },
        {
            "readable": "Thermocouple 8",
            "port": "8",
        },
    ],
}


class DataController(object):
    def __init__(self, path):
        logger.info("Initializing Pico TC-08 Temperature plugin")

        self.name = DEFAULT_CONFIG["name"]
        with open(join(path, "plugins",
                       f"{self.name}.json")) as file:
            self.config = json.load(file)

    def match_source_attributes(self, source):
        for attr in self.config["Sources"]:
            if attr["readable"] == source or attr["port"] == source:
                return attr
        logger.critical("Could not match plugin source.")
        return None

    def read(self, source):
        attr = self.match_source_attributes(source)
        if attr:
            print(f"Reading from port {attr['port']}")
            return 0
        return None
