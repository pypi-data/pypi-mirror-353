import unittest
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mv0401.mv0401 import MV0401_Device


class TestMV0401(unittest.TestCase):
    """Test cases for MV0401 device wrapper"""

    def setUp(self):
        """Set up test cases"""
        self.device = MV0401_Device("10.0.110.204")
        self.device.connect()

    def tearDown(self):
        """Clean up after test cases"""
        self.device.disconnect()

    def test_get_ip(self):
        """Test GET IPADDR command"""
        response = self.device.get_ip()
        self.assertIsInstance(response, dict)
        self.assertEqual(response["command"], "GET IPADDR")
        self.assertIn("ip", response)
        self.assertIn("subnet", response)
        self.assertIn("gateway", response)
        self.assertIsInstance(response["ip"], str)
        self.assertIsInstance(response["subnet"], str)
        self.assertIsInstance(response["gateway"], str)

    def test_get_version(self):
        """Test GET VER command"""
        response = self.device.get_version()
        self.assertIsInstance(response, dict)
        self.assertEqual(response["command"], "GET VER")
        self.assertIn("version", response)
        self.assertIsInstance(response["version"], str)
        self.assertTrue(response["version"].startswith("v"))

    def test_get_mac(self):
        """Test GET MAC command"""
        response = self.device.get_mac()
        self.assertIsInstance(response, dict)
        self.assertEqual(response["command"], "GET MAC")
        self.assertIn("mac", response)
        self.assertIsInstance(response["mac"], str)
        # MAC address format: XX:XX:XX:XX:XX:XX
        self.assertTrue(len(response["mac"].split(":")) == 6)

    def test_get_layout(self):
        """Test GET VIDOUT_MODE command"""
        response = self.device.get_layout()
        self.assertIsInstance(response, dict)
        self.assertEqual(response["command"], "GET VIDOUT_MODE")
        self.assertIn("mode", response)
        self.assertIsInstance(response["mode"], int)
        self.assertIn(response["mode"], [0, 1, 2, 3, 4, 5])  # Valid layout modes

    def test_get_vid_res(self):
        """Test GET VIDOUT_RES command"""
        response = self.device.get_vid_res()
        self.assertIsInstance(response, dict)
        self.assertEqual(response["command"], "GET VIDOUT_RES")
        self.assertIn("resolution", response)
        self.assertIsInstance(response["resolution"], int)
        self.assertIn(response["resolution"], [0, 1, 2, 3])  # Valid resolution modes

    def test_get_audout_chan(self):
        """Test GET AUDOUT_SRC command"""
        response = self.device.get_audout_chan()
        self.assertIsInstance(response, dict)
        self.assertEqual(response["command"], "GET AUDOUT_SRC")
        self.assertIn("source", response)
        self.assertIsInstance(response["source"], int)
        self.assertIn(response["source"], [1, 2, 3, 4])  # Valid audio sources

    def test_get_audout_window(self):
        """Test GET AUDOUT_WND command"""
        response = self.device.get_audout_window()
        self.assertIsInstance(response, dict)
        self.assertEqual(response["command"], "GET AUDOUT_WND")
        self.assertIn("window", response)
        self.assertIsInstance(response["window"], int)
        self.assertIn(response["window"], [1, 2, 3, 4])  # Valid window numbers

    def test_get_osd(self):
        """Test GET OSD command"""
        response = self.device.get_osd()
        self.assertIsInstance(response, dict)
        self.assertEqual(response["command"], "GET OSD")
        self.assertIn("enabled", response)
        self.assertIsInstance(response["enabled"], bool)

    def test_get_osd_time(self):
        """Test GET OSD_T command"""
        response = self.device.get_osd_time()
        self.assertIsInstance(response, dict)
        self.assertEqual(response["command"], "GET OSD_T")
        self.assertIn("timeout", response)
        self.assertIsInstance(response["timeout"], int)
        self.assertTrue(3 <= response["timeout"] <= 10)  # Valid timeout range

    def test_get_input_valid(self):
        """Test GET VIDIN_VALID command for all inputs"""
        for input_num in range(1, 5):
            response = self.device.get_input_valid(input_num)
            self.assertIsInstance(response, dict)
            self.assertEqual(response["command"], "GET VIDIN_VALID")
            self.assertIn("input", response)
            self.assertIn("valid", response)
            self.assertIsInstance(response["input"], int)
            self.assertIsInstance(response["valid"], bool)
            self.assertEqual(response["input"], input_num)

    def test_get_input_video_info(self):
        """Test GET VIDIN_INFO command for all inputs"""
        for input_num in range(1, 5):
            response = self.device.get_input_video_info(input_num)
            self.assertIsInstance(response, dict)
            self.assertEqual(response["command"], "GET VIDIN_INFO")
            self.assertIn("timing", response)
            self.assertIn("color_space", response)
            self.assertIn("color_depth", response)
            self.assertIsInstance(response["timing"], str)
            self.assertIsInstance(response["color_space"], str)
            self.assertIsInstance(response["color_depth"], str)

    def test_get_audin_info(self):
        """Test GET AUDIN_INFO command for all inputs"""
        for input_num in range(1, 5):
            response = self.device.get_audin_info(input_num)
            self.assertIsInstance(response, dict)
            self.assertEqual(response["command"], "GET AUDIN_INFO")
            self.assertIn("format", response)
            self.assertIn("channels", response)
            self.assertIn("sample_rate", response)
            self.assertIsInstance(response["format"], str)
            self.assertIsInstance(response["channels"], str)
            self.assertIsInstance(response["sample_rate"], str)

    def test_get_vidout_info(self):
        """Test GET VIDOUT_INFO command"""
        response = self.device.get_vidout_info()
        self.assertIsInstance(response, dict)
        self.assertEqual(response["command"], "GET VIDOUT_INFO")
        self.assertIn("timing", response)
        self.assertIn("color_space", response)
        self.assertIn("color_depth", response)
        self.assertIsInstance(response["timing"], str)
        self.assertIsInstance(response["color_space"], str)
        self.assertIsInstance(response["color_depth"], str)

    def test_get_audout_info(self):
        """Test GET AUDOUT_INFO command for both outputs"""
        for output_num in [0, 1]:  # 0: HDMI out, 1: AV out
            response = self.device.get_audout_info(output_num)
            self.assertIsInstance(response, dict)
            self.assertEqual(response["command"], "GET AUDOUT_INFO")
            self.assertIn("format", response)
            self.assertIn("channels", response)
            self.assertIn("sample_rate", response)
            self.assertIsInstance(response["format"], str)
            self.assertIsInstance(response["channels"], str)
            self.assertIsInstance(response["sample_rate"], str)


if __name__ == "__main__":
    unittest.main()
