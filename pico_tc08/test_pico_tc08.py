import unittest
import cyp_pico_tc08
from picosdk.errors import PicoSDKCtypesError


class TestIndependantMethods(unittest.TestCase):
    def test_check_api_response_type(self):
        self.assertRaises(TypeError, cyp_pico_tc08.check_api_response, "Resp")
        self.assertRaises(TypeError, cyp_pico_tc08.check_api_response, True)
        self.assertRaises(TypeError, cyp_pico_tc08.check_api_response, 7+2j)
        self.assertRaises(TypeError, cyp_pico_tc08.check_api_response, 0.456)

    def test_check_api_response_passthrough(self):
        self.assertEqual(cyp_pico_tc08.check_api_response(1), 1)
        self.assertEqual(cyp_pico_tc08.check_api_response(13), 13)

    def test_check_api_response_error(self):
        self.assertRaises(PicoSDKCtypesError,
                          cyp_pico_tc08.check_api_response, 0)
        self.assertRaises(PicoSDKCtypesError,
                          cyp_pico_tc08.check_api_response, -5)

    """
    def test_autonomous_read_all(self):
        data = cyp_pico_tc08.autonomous_read_all()
        self.assertIs(type(data), dict)

        for point in data:
            self.assertIs(type(point), str)
            self.assertIs(type(data[point]), float)
            self.assertTrue(-270 <= data[point] <= 1820)
    """


class TestPicoController(unittest.TestCase):
    def setUp(self):
        self.controller = cyp_pico_tc08.PicoController()

    def tearDown(self):
        self.controller.cleanup()

    def test_attributes(self):
        self.assertIs(type(self.controller.name), str)
        self.assertLogs(self.controller.logger, "DEBUG")

    def test_devices(self):
        self.assertIs(type(self.controller.devices), list)
        self.assertTrue(len(self.controller.devices) > 0)
        for device in self.controller.devices:
            self.assertIs(type(device), int)
            self.assertTrue(device > 0)

    def test_sources(self):
        self.assertIs(type(self.controller.sources), dict)
        print(len(self.controller.sources))
        self.assertEqual(len(self.controller.sources) % 8, 0)
        for key, object in self.controller.sources.items():
            self.assertIs(type(key), str)
            self.assertIs(type(object), cyp_pico_tc08.PicoChannel)


class TestProfile(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
