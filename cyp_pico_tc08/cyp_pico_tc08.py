import logging
from random import randint
from cyckei.plugins import cyp_base

logger = logging.getLogger("cyckei")


class PicoController(cyp_base.PluginController):
    def __init__(self):
        super().__init__()

    def get_sources(self):
        """
        Searches for available sources, and establishes source objects.

        Returns
        -------
        Dictionary of sources in format "name": SourceObject.
        """

        # Sources don't need to be found for this plugin,
        # so we just initialize two randomizers as examples
        sources = {}
        sources["Rand1"] = PicoChannel(1)
        sources["Rand2"] = PicoChannel(2)

        return sources


class PicoChannel(cyp_base.SourceObject):
    def __init__(self, port):
        super().__init__()
        self.range = [0, port]
        self.name = f"Random 0-{port}"

    def read(self):
        return randint(self.range[0], self.range[1])


if __name__ == "__main__":
    controller = PicoController()
    print(cyp_base.read_all(controller))
