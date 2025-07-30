import time
from telnetlib import Telnet
import select
import socket
from typing import Optional, Dict, Any


class MV0401_Device:
    """Python wrapper using Telnet control"""

    def __init__(
        self, ip: str, port: int = 23, timeout: float = 1.0, max_retries: int = 3
    ) -> None:
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.max_retries = max_retries
        self.tn: Optional[Telnet] = None
        self._last_connection_time: float = 0
        self._connection_attempts: int = 0
        self._is_connected: bool = False

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the raw response from the device into a structured format.

        Args:
            response (str): Raw response from the device

        Returns:
            Dict[str, Any]: Structured response data
        """
        if response.startswith("Failed"):
            return {"error": response}

        # Split the response into command and parameters
        parts = response.strip().split()
        if not parts:
            return {"error": "Empty response"}

        command = parts[0]
        params = parts[1:]

        # Determine if this is a GET or SET command
        command_type = (
            "GET"
            if command
            in [
                "IPADDR",
                "VER",
                "MAC",
                "VIDOUT_MODE",
                "VIDOUT_RES",
                "AUDOUT_SRC",
                "AUDOUT_WND",
                "OSD",
                "OSD_T",
                "VIDIN_VAILD",
                "VIDIN_INFO",
                "AUDIN_INFO",
                "VIDOUT_INFO",
                "AUDOUT_INFO",
            ]
            else "SET"
        )

        # Create base response structure
        result = {"command": f"{command_type} {command}"}

        # Layout mode mapping
        layout_modes = {
            "0": "Original",
            "1": "Dual-view",
            "2": "PiP",
            "3": "H Mode",
            "4": "Master",
            "5": "Quad",
        }

        # Video resolution mapping
        resolution_modes = {
            "0": "Follow Sink",
            "1": "4K@60",
            "2": "4K@30",
            "3": "1080p@60",
        }

        # Audio format mapping
        audio_formats = {
            "0": "PCM",
            "1": "Dolby Digital",
            "2": "DTS",
            "3": "AAC",
            "4": "MP3",
        }

        # Add parameters based on command type
        if command == "IPADDR":
            if len(params) >= 3:
                result.update(
                    {"ip": params[0], "subnet": params[1], "gateway": params[2]}
                )
        elif command == "VER":
            if params:
                result.update({"version": params[0]})
        elif command == "MAC":
            if params:
                result.update({"mac": params[0]})
        elif command == "VIDOUT_MODE":
            if params:
                mode = params[0]
                result.update({"mode": layout_modes.get(mode, mode)})
        elif command == "VIDOUT_RES":
            if params:
                res = params[0]
                result.update({"resolution": resolution_modes.get(res, res)})
        elif command == "AUDOUT_SRC":
            if params:
                result.update({"source": f"HDMI Input {params[0]}"})
        elif command == "AUDOUT_WND":
            if params:
                result.update({"window": f"Window {params[0]}"})
        elif command == "OSD":
            if params:
                result.update({"enabled": bool(int(params[0]))})
        elif command == "OSD_T":
            if params:
                result.update({"timeout": int(params[0])})
        elif command == "VIDIN_VAILD":
            if len(params) >= 2:
                result.update(
                    {"input": f"HDMI Input {params[0]}", "valid": bool(int(params[1]))}
                )
        elif command == "VIDIN_INFO":
            # Expected: VIDIN_INFO <input> <timing> <color_space> <color_depth>
            if len(params) >= 4:
                result.update(
                    {
                        "input": f"HDMI Input {params[0]}",
                        "timing": params[1],
                        "color_space": params[2],
                        "color_depth": params[3],
                    }
                )
            elif len(params) == 3:
                # Some firmware may omit input number
                result.update(
                    {
                        "timing": params[0],
                        "color_space": params[1],
                        "color_depth": params[2],
                    }
                )
        elif command == "AUDIN_INFO":
            # Expected: AUDIN_INFO <input> <format> <channels> <sample_rate>
            if len(params) >= 4:
                fmt = params[1]
                if fmt in audio_formats:
                    fmt = audio_formats[fmt]
                result.update(
                    {
                        "input": f"HDMI Input {params[0]}",
                        "format": fmt,
                        "channels": params[2],
                        "sample_rate": params[3],
                    }
                )
            elif len(params) == 3:
                fmt = params[0]
                if fmt in audio_formats:
                    fmt = audio_formats[fmt]
                result.update(
                    {"format": fmt, "channels": params[1], "sample_rate": params[2]}
                )
        elif command == "VIDOUT_INFO":
            # Expected: VIDOUT_INFO <timing> <color_space> <color_depth>
            if len(params) >= 3:
                result.update(
                    {
                        "timing": params[0],
                        "color_space": params[1],
                        "color_depth": params[2],
                    }
                )
        elif command == "AUDOUT_INFO":
            # Expected: AUDOUT_INFO <output> <format> <channels> <sample_rate>
            if len(params) >= 4:
                fmt = params[1]
                if fmt in audio_formats:
                    fmt = audio_formats[fmt]
                result.update(
                    {
                        "output": f"Audio Out {params[0]}",
                        "format": fmt,
                        "channels": params[2],
                        "sample_rate": params[3],
                    }
                )
            elif len(params) == 3:
                fmt = params[0]
                if fmt in audio_formats:
                    fmt = audio_formats[fmt]
                result.update(
                    {"format": fmt, "channels": params[1], "sample_rate": params[2]}
                )
        else:
            # For unknown commands, include all parameters
            result["parameters"] = params

        return result

    def connect(self) -> bool:
        """
        Attempts to connect to the device, handling cases where the device might be offline or not responding.

        Returns:
            bool: True if connection was successful, False otherwise
        """
        if self._is_connected and self.tn is not None:
            try:
                # Test if connection is still alive
                self.tn.get_socket().send(b"")
                return True
            except (socket.error, AttributeError):
                self._is_connected = False
                self.tn = None

        try:
            self.tn = Telnet()
            self.tn.open(self.ip, self.port, timeout=self.timeout)
            # Wait for initial response
            response = self.tn.read_until(b"\r\n", timeout=self.timeout)
            if response:
                self._is_connected = True
                self._last_connection_time = time.time()
                self._connection_attempts = 0
                return True
            else:
                raise ConnectionError("No response from device")
        except (socket.error, ConnectionError) as e:
            print(f"Failed to connect to {self.ip}:{self.port}. Error: {e}")
            self._is_connected = False
            self.tn = None
            return False

    def ensure_connection(self) -> bool:
        """
        Ensures that the device is connected before sending commands.
        Implements exponential backoff for reconnection attempts.

        Returns:
            bool: True if connection is established, False otherwise
        """
        if self._is_connected and self.tn is not None:
            try:
                # Test if connection is still alive
                self.tn.get_socket().send(b"")
                return True
            except (socket.error, AttributeError):
                self._is_connected = False
                self.tn = None

        # Implement exponential backoff
        if self._connection_attempts < self.max_retries:
            wait_time = min(2**self._connection_attempts, 30)  # Cap at 30 seconds
            time.sleep(wait_time)
            self._connection_attempts += 1
            return self.connect()

        return False

    def send(self, message: str) -> Dict[str, Any]:
        """
        Sends a message to the Controller and returns the response in a structured format.

        Args:
            message (str): The command to send to the device

        Returns:
            Dict[str, Any]: Structured response from the device
        """
        if not self.ensure_connection():
            return {"error": "Failed to establish connection"}

        try:
            message_bytes = f"{message}\n".encode()
            self.tn.write(message_bytes)
            stdout = self.tn.read_until(b"\r\n", timeout=self.timeout).decode()
            response = stdout.strip(">")
            return self._parse_response(response)
        except (socket.error, ConnectionError) as e:
            print(f"Failed to send command to {self.ip}. Error: {e}")
            self._is_connected = False
            self.tn = None
            return {"error": f"Failed to send command: {e}"}

    def send_long(self, message: str, timeout: int = 2) -> Dict[str, Any]:
        """
        Sends a message to the Controller and reads the response until a timeout.
        Returns the response in a structured format.

        Args:
            message (str): The command to send to the device
            timeout (int): Maximum time to wait for response in seconds

        Returns:
            Dict[str, Any]: Structured response from the device
        """
        if not self.ensure_connection():
            return {"error": "Failed to establish connection"}

        try:
            message_bytes = f"{message}\n".encode()
            self.tn.write(message_bytes)

            start_time = time.time()
            response_data = b""

            while (time.time() - start_time) < timeout:
                ready, _, _ = select.select([self.tn.get_socket()], [], [], 0.1)
                if ready:
                    data = self.tn.read_very_eager()
                    response_data += data
                    if not data:
                        break

            response = response_data.decode("utf-8").strip()
            return self._parse_response(response)
        except (socket.error, ConnectionError) as e:
            print(f"Failed to send command to {self.ip}. Error: {e}")
            self._is_connected = False
            self.tn = None
            return {"error": f"Failed to send command: {e}"}

    def disconnect(self) -> None:
        """
        Safely closes the Telnet connection if it exists.
        """
        if self.tn is not None:
            try:
                self.tn.close()
            except Exception as e:
                print(f"Error closing Telnet connection: {e}")
            finally:
                self.tn = None
                self._is_connected = False

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()

    def get_version(self) -> Dict[str, str]:
        """Get the firmware version of the device.

        Returns:
            Dict[str, str]: Dictionary containing version information
        """
        return self.send("GET VER")

    def set_vid_mute(self, prm1, prm2):
        """description: set video mute status
        command: SET VIDOUT_MUTE prm1 prm2
        return: VIDOUT_MUTE prm1 prm2
        parameters:
          prm1:
            description: input you want to apply video mute
            values:
              0: hdmi output
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
          prm2:
            description: muted or unmuted status
            values:
              0: un-muted
              1: muted
        example:
          request: SET VIDOUT_MUTE 1 1
          return: VIDOUT_MUTE 1 1"""

        return self.send(f"SET VIDOUT_MUTE {prm1} {prm2}")

    def get_vid_mute(self, prm1):
        """description: get the video mute status
        command: GET VIDOUT_MUTE prm1
        return: VIDOUT_MUTE prm1 prm2
        parameters:
          prm1:
            description: hdmi input
            values:
              0: hdmi output
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
          prm2:
            description: mute status
            values:
              0: un-muted
              1: muted
        example:
          request: GET VIDOUT_MUTE 1
          return: VIDOUT_MUTE 1 1
          description: the result is hdmi in1 is set to mute"""

        return self.send(f"GET VIDOUT_MUTE {prm1}")

    def set_vid_res(self, prm1):
        """description: set the video output resolution
        command: SET VIDOUT_RES prm1
        return: VIDOUT_RES prm1
        parameters:
          prm1:
            description: the resolution to be set
            values:
              0: follow sink preferred timing
              1: force 4k@60
              2: force 4k@30
              3: force 1080p@60
        example:
          request: SET VIDOUT_RES 0
          return: VIDOUT_RES 0
          description: set the video output resolution mode to follow sink preferred timing
        """

        return self.send(f"SET VIDOUT_RES {prm1}")

    def get_vid_res(self) -> Dict[str, int]:
        """Get the current video output resolution mode.

        Returns:
            Dict[str, int]: Dictionary containing resolution mode
        """
        return self.send("GET VIDOUT_RES")

    def set_layout(self, prm1):
        """description: change which layout you want displayed
        command: SET VIDOUT_MODE prm1
        return: VIDOUT_MODE prm1
        parameters:
          prm1:
            description: layout
            values:
              0: Original
              1: Dual-view
              2: PiP
              3: H mode
              4: Master
              5: Quad
        example:
          request: SET VIDOUT_MODE 0
          return: VIDOUT_MODE 0
          description: set layout to Original which will be a single image"""

        if prm1:
            return self.send(f"SET VIDOUT_MODE {prm1}")
        else:
            return self.send("SET VIDOUT_MODE")

    def get_layout(self) -> Dict[str, int]:
        """Get the current layout mode.
        prm = {0,1,2,3,4,5}
        // 0: Original
        // 1: Dual-view
        // 2: Pip
        // 3: 'H' Mode
        // 4: Master
        // 5: Quad


        Returns:
            Dict[str, int]: Dictionary containing layout mode
        """
        return self.send("GET VIDOUT_MODE")

    def set_layout_original(self, prm1):
        """description: select which source to be used while in Original Layout mode
        command: SET VIDOUT_ORIGINAL_SRC prm1
        return: VIDOUT_ORIGINAL_SRC prm1
        parameters:
          prm1:
            description: layout
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
        example:
          request: SET VIDOUT_ORIGINAL_SRC 1
          return: VIDOUT_ORIGINAL_SRC 1
          description: Sets hdmi in1 as the source for Original Layout"""

        return self.send(f"SET VIDOUT_ORIGINAL_SRC {prm1}")

    def get_layout_original(self):
        """description: get which source is being used in Original Layout mode
        command: GET VIDOUT_ORIGINAL_SRC
        return: VIDOUT_ORIGINAL_SRC prm1
        parameters:
          prm1:
            description: layout
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
        example:
          request: GET VIDOUT_ORIGINAL_SRC
          return: VIDOUT_ORIGINAL_SRC 1 # Error in PDF
          description: hdmi in1 is currently selected on the Original Layout mode"""

        return self.send("GET VIDOUT_ORIGINAL_SRC")

    def set_layout_dual(self, prm1, prm2):
        """description: select which sources to be used in dual layout mode
        command: SET VIDOUT_DUAL_SRC prm1 prm2
        return: VIDOUT_DUAL_SRC prm1 prm2
        parameters:
          prm1:
            description: left channel
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
          prm2:
            description: right channel
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
        example:
          request: SET VIDOUT_DUAL_SRC 1 2
          return: VIDOUT_DUAL_SRC 1 2
          description: Display is split into 2 images. Left is on hdmi in1 and Right is on hdmi in2
        """

        return self.send(f"SET VIDOUT_DUAL_SRC {prm1} {prm2}")

    def get_layout_dual(self):
        """description: get which sources are currently set for Dual Layout mode
        command: GET VIDOUT_DUAL_SRC
        return: VIDOUT_DUAL_SRC prm1 prm2
        parameters:
          prm1:
            description: left channel
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
          prm2:
            description: right channel
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
        example:
          request: GET VIDOUT_DUAL_SRC
          return: VIDOUT_DUAL_SRC 1 2
          description: hdmi in1 is on left channel and hdmi in2 is on right channel"""

        return self.send("GET VIDOUT_DUAL_SRC")

    def set_layout_h(self, prm1, prm2, prm3, prm4):
        """description: set video sources for H Layout mode
        command: SET VIDOUT_H_SRC prm1 prm2 prm3 prm4
        return: VIDOUT_H_SRC prm1 prm2 prm3 prm4
        parameters:
          prm1:
            description: left channel
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
          prm2:
            description: top middle channel
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
          prm3:
            description: bottom middle channel
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
          prm4:
            description: right channel
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
        example:
          request: SET VIDOUT_H_SRC 1 2 3 4
          return: VIDOUT_H_SRC 1 2 3 4
          description: set hdmi in1 to left channel, hdmi in2 to top middle channel, hdmi in3 to bottom middle channel, hdmi in4 to right channel
        """

        return self.send(f"SET VIDOUT_H_SRC {prm1} {prm2} {prm3} {prm4}")

    def get_layout_h(self):
        """description: get video sources in the H Layout mode
        command: GET VIDOUT_H_SRC
        return: VIDOUT_H_SRC prm1 prm2 prm3 prm4
        parameters:
          prm1:
            description: left channel
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
          prm2:
            description: top middle channel
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
          prm3:
            description: bottom middle channel
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
          prm4:
            description: right channel
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
        example:
          request: GET VIDOUT_H_SRC
          return: VIDOUT_H_SRC 1 2 3 4
          description: hdmi in1 to left channel, hdmi in2 to top middle channel, hdmi in3 to bottom middle channel, hdmi in4 to right channel
        """

        return self.send("GET VIDOUT_H_SRC")

    def set_layout_pip(self, prm1, prm2):
        """description: set the sources for PiP layout mode
        command: SET VIDOUT_PIP_SRC prm1 prm2
        return: VIDOUT_PIP_SRC prm1 prm2
        parameters:
          prm1:
            description: big channel
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
          prm2:
            description: small channel
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
        example:
          request: SET VIDOUT_PIP_SRC 1 2
          return: VIDOUT_PIP_SRC 1 2
          description: set hdmi in1 to the big channel, set hdmi in2 to the small channel
        """

        return self.send(f"SET VIDOUT_PIP_SRC {prm1} {prm2}")

    def get_layout_pip(self):
        """description: get the sources for the PiP Layout mode
        command: GET VIDOUT_PIP_SRC
        return: VIDOUT_PIP_SRC prm1 prm2
        parameters:
          prm1:
            description: big channel
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
          prm2:
            description: small channel
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
        example:
          request: GET VIDOUT_PIP_SRC
          return: VIDOUT_PIP_SRC 1 2
          description: hdmi in1 to the big channel, set hdmi in2 to the small channel"""

        return self.send("GET VIDOUT_PIP_SRC")

    def set_layout_quad(self, prm1, prm2, prm3, prm4):
        """description: Set the video sources in quad mode
        command: SET VIDOUT_QUAD_SRC prm1 prm2 prm3 prm4
        return: VIDOUT_QUAD_SRC prm1 prm2 prm3 prm4
        parameters:
          prm1:
            description: top left channel
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
          prm2:
            description: top right channel
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
          prm3:
            description: bottom left channel
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
          prm4:
            description: bottom right channel
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
        example:
          request: SET VIDOUT_QUAD_SRC 1 2 3 4
          return: VIDOUT_QUAD_SRC 1 2 3 4
          description: in1 to top left, in2 to top right, in3 to bottom left, in4 to bottom right
        """

        return self.send(f"SET VIDOUT_QUAD_SRC {prm1} {prm2} {prm3} {prm4}")

    def get_layout_quad(self):
        """description: get video source and locations in Quad Layout mode
        command: GET VIDOUT_QUAD_SRC
        return: VIDOUT_QUAD_SRC prm1 prm2 prm3 prm4
        parameters:
          prm1:
            description: top left channel
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
          prm2:
            description: top right channel
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
          prm3:
            description: bottom left channel
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
          prm4:
            description: bottom right channel
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
        example:
          request: GET VIDOUT_QUAD_SRC
          return: VIDOUT_QUAD_SRC 1 2 3 4
          description: in1 to top left, in2 to top right, in3 to bottom left, in4 to bottom right
        """

        return self.send("GET VIDOUT_QUAD_SRC")

    def set_layout_master(self, prm1, prm2, prm3, prm4):
        """description: set the video sources for Master Layout mode
        command: SET VIDOUT_MASTER_SRC prm1 prm2 prm3 prm4
        return: VIDOUT_MASTER_SRC prm1 prm2 prm3 prm4
        parameters:
          prm1:
            description: left channel
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
          prm2:
            description: top right channel
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
          prm3:
            description: middle right channel
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
          prm4:
            description: bottom right channel
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
        example:
          request: SET VIDOUT_MASTER_SRC 1 2 3 4
          return: VIDOUT_MASTER_SRC 1 2 3 4
          description: in1 to left, in2 to top right, in3 to middle right, in4 to bottom right
        """

        return self.send(f"SET VIDOUT_MASTER_SRC {prm1} {prm2} {prm3} {prm4}")

    def get_layout_master(self):
        """description: get the video sources for Master Layout mode
        command: GET VIDOUT_MASTER_SRC
        return: VIDOUT_MASTER_SRC prm1 prm2 prm3 prm4
        parameters:
          prm1:
            description: left channel
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
          prm2:
            description: top right channel
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
          prm3:
            description: middle right channel # Error in PDF
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
          prm4:
            description: bottom right channel
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
        example:
          request: GET VIDOUT_MASTER_SR
          return: VIDOUT_MASTER_SRC 1 2 3 4
          description: in1 to left, in2 to top right, in3 to middle right, in4 to bottom right
        """

        return self.send("GET VIDOUT_MASTER_SR")

    def set_audout_chan(self, prm1):
        """description: set the audio output channel
        command: SET AUDOUT_SRC prm1
        return: AUDOUT_SRC prm1
        parameters:
          prm1:
            description: hdmi input
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
        example:
          request: SET AUDOUT_SRC 1
          return: AUDOUT_SRC 1
          description: Set hdmi in1 as audio output"""

        return self.send(f"SET AUDOUT_SRC {prm1}")

    def get_audout_chan(self) -> Dict[str, int]:
        """Get the current audio output channel.

        Returns:
            Dict[str, int]: Dictionary containing audio output channel
        """
        return self.send("GET AUDOUT_SRC")

    def set_audout_window(self, prm1):
        """description: set the audio output window
        command: SET AUDOUT_WND prm1
        return: AUDOUT_WND prm1
        parameters:
          prm1:
            description: window
            values:
              1: window 1
              2: window 2
              3: window 3
              4: window 4
        example:
          request: SET AUDOUT_WND 1
          return: AUDOUT_WND 1
          description: Audio output is set to window 1"""

        return self.send(f"SET AUDOUT_WND {prm1}")

    def get_audout_window(self) -> Dict[str, int]:
        """Get the current audio output window.

        Returns:
            Dict[str, int]: Dictionary containing audio output window
        """
        return self.send("GET AUDOUT_WND")

    def set_audout_chan_mute(self, prm1, prm2):
        """description: set the audio output channel mute status
        command: SET AUDOUT_MUTE prm1 prm2
        return: AUDOUT_MUTE prm1 prm2
        parameters:
          prm1:
            description: output
            values:
              0: hdmi out
              1: av out
          prm2:
            description: mute status
            values:
              0: un-mute
              1: mute
        example:
          request: SET AUDOUT_MUTE 0 0
          return: AUDOUT_MUTE 0 0
          description: Sets the hdmi out to un-muted"""

        return self.send(f"SET AUDOUT_MUTE {prm1} {prm2}")

    def get_audout_chan_mute(self, prm1):
        """description: get the audio output channel mute status
        command: GET AUDOUT_MUTE prm1
        return: AUDOUT_MUTE prm1 prm2
        parameters:
          prm1:
            description: output
            values:
              0: hdmi out
              1: av out
          prm2:
            description: mute status
            values:
              0: un-mute
              1: mute
        example:
          request: GET AUDOUT_MUTE 0
          return: AUDOUT_MUTE 0 0
          description: hdmi out is currently un-muted"""

        return self.send(f"GET AUDOUT_MUTE {prm1}")

    def set_input_stretch(self, prm1, prm2):
        """description: set the input video stretch status
        command: SET VIDIN_STRETCH prm1 prm2
        return: VIDIN_STRETCH prm1 prm2
        parameters:
          prm1:
            description: input
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
          prm2:
            description: stretch status
            values:
              0: original
              1: full
        example:
          request: SET VIDIN_STRETCH 1 0
          return: VIDIN_STRETCH 1 0
          description: Sets hdmi in1 to original"""
        return self.send(f"SET VIDIN_STRETCH {prm1} {prm2}")

    def get_input_stretch(self, prm1):
        """description: get the input video stretch status
        command: GET VIDIN_STRETCH prm1
        return: VIDIN_STRETCH prm1 prm2
        parameters:
          prm1:
            description: input
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
          prm2:
            description: stretch status
            values:
              0: original
              1: full
        example:
          request: GET VIDIN_STRETCH 1
          return: VIDIN_STRETCH 1 0
          description: hdmi in1 is set to original"""

        return self.send(f"GET VIDIN_STRETCH {prm1}")

    def set_input_video(self, prm1, prm2):
        """description: set hdcp support for input
        command: SET VIDIN_HDCP_CAP prm1 prm2
        return: VIDIN_HDCP_CAP prm1 prm2
        parameters:
          prm1:
            description: input
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
          prm2:
            description: hdcp support
            values:
              0: hdcp 2.2 + 1.4
              1: hdcp 1.4
              2: no hdcp support
        example:
          request: SET VIDIN_HDCP_CAP 1 0
          return: VIDIN_HDCP_CAP 1 0
          description: hdmi in1 is set to hdcp 2.2 & 1.4 support"""

        return self.send(f"SET VIDIN_HDCP_CAP {prm1} {prm2}")

    def get_input_video(self, prm1):
        """description: get hdcp support for input
        command: GET VIDIN_HDCP_CAP prm1
        return: VIDIN_HDCP_CAP prm1 prm2
        parameters:
          prm1:
            description: input
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
          prm2:
            description: hdcp support
            values:
              0: hdcp 2.2 + 1.4
              1: hdcp 1.4
              2: no hdcp support
        example:
          request: GET VIDIN_HDCP_CAP 1
          return: VIDIN_HDCP_CAP 1 0
          description: hdmi in1 is set to hdcp 2.2 & 1.4 support"""

        return self.send(f"GET VIDIN_HDCP_CAP {prm1}")

    def set_input_edid(self, prm1, prm2):
        """description: select or copy edid
        command: SET VIDIN_EDID_MODE prm1 prm2
        return: VIDIN_EDID_MODE prm1 prm2
        parameters:
          prm1:
            description: input
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
          prm2:
            description: edid mode
            values:
              0: copy from hdmi out
              1: customer edid
              2: 4k@60 7.1 with dolby vision
              3: 4k@60 7.1 with hdr10
              4: 4k@60 7.1 with sdr
              5: 1080p@60 with 7.1
              6: 1080p@60 with 2.0
        example:
          request: SET VIDIN_EDID_MODE 1 0
          return: VIDIN_EDID_MODE 1 0
          description: hdmi in1 is set to copy edid from hdmi out"""

        return self.send(f"SET VIDIN_EDID_MODE {prm1} {prm2}")

    def get_input_hdcp(self, prm1):
        """description: get hdcp support for input
        command: GET VIDIN_HDCP_CAP prm1
        return: VIDIN_HDCP_CAP prm1 prm2
        parameters:
          prm1:
            description: input
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
          prm2:
            description: hdcp support
            values:
              0: hdcp 2.2 + 1.4
              1: hdcp 1.4
              2: no hdcp support
        example:
          request: GET VIDIN_HDCP_CAP 1
          return: VIDIN_HDCP_CAP 1 0
          description: hdmi in1 is set to hdcp 2.2 & 1.4 support"""

        return self.send(f"GET VIDIN_HDCP_CAP {prm1}")

    def set_input_edid_custom(self, prm1, prm2):
        """description: set custom edid using hex data
        command: SET VIDIN_EDID_CUS prm1 prm2
        return: VIDIN_EDID_CUS prm1 prm2
        parameters:
          prm1:
            description: input
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
          prm2:
            description: 512 bytes edid ascii data with no spaces (hex data need conversion into ASCII code)
            values:
              edid: 512 bytes edid ascii data
        example:
          request: SET VIDIN_EDID_CUS 1 XX...XX
          return: VIDIN_EDID_CUS 1 XX...XX
          description: write EDID content into hdmi in1"""

        return self.send(f"SET VIDIN_EDID_CUS {prm1} {prm2}")

    def get_input_edid_custom(self, prm1):
        """description: get custom edid using hex data
        command: GET VIDIN_EDID_CUS prm1
        return: VIDIN_EDID_CUS prm1 prm2
        parameters:
          prm1:
            description: input
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
          prm2:
            description: 512 bytes edid ascii data with no spaces (hex data need conversion into ASCII code)
            values:
              edid: 512 bytes edid ascii data
        example:
          request: GET VIDIN_EDID_CUS 1
          return: VIDIN_EDID_CUS 1 XX...XX
          description: read EDID content from hdmi in1"""

        return self.send(f"GET VIDIN_EDID_CUS {prm1}")

    def get_input_edid(self, prm1):
        """description: get the current input edid information
        command: GET VIDIN_EDID_CUR prm1
        return: VIDIN_EDID_CUS prm1 prm2
        parameters:
          prm1:
            description: input
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
          prm2:
            description: 512 bytes edid ascii data with no spaces (hex data need conversion into ASCII code)
            values:
              edid: 512 bytes edid ascii data
        example:
          request: GET VIDIN_EDID_CUR 1
          return: VIDIN_EDID_CUR 1 XX...XX
          description: read current edid from hdmi in1"""

        return self.send(f"GET VIDIN_EDID_CUR {prm1}")

    def set_layout_pip_location(self, prm1):
        """description: sets the location of the PiP window
        command: SET VIDOUT_PIP_POS prm1
        return: VIDOUT_PIP_POS prm1
        parameters:
          prm1:
            description: location
            values:
              0: top left
              1: top right
              2: bottom left
              3: bottom right
        example:
          request: SET VIDOUT_PIP_POS 0
          return: VIDOUT_PIP_POS 0
          description: move PiP small window to top left"""

        return self.send(f"SET VIDOUT_PIP_POS {prm1}")

    def get_layout_pip_location(self):
        """description: gets the location of the PiP window
        command: GET VIDOUT_PIP_POS
        return: VIDOUT_PIP_POS prm1
        parameters:
          prm1:
            description: location
            values:
              0: top left
              1: top right
              2: bottom left
              3: bottom right
        example:
          request: GET VIDOUT_PIP_POS
          return: VIDOUT_PIP_POS 0
          description: tells you the location of the PiP window in in the top left"""

        return self.send("GET VIDOUT_PIP_POS")

    def set_layout_pip_size(self, prm1):
        """description: adjust the distance of the small window
        command: SET VIDOUT_PIP_SIZE prm1
        return: VIDOOUT_PIP_SIZE prm1
        parameters:
          prm1:
            description: size
            values:
              0: 1/4
              1: 1/9
              2: 1/16
        example:
          request: SET VIDOUT_PIP_SIZE 0
          return: VIDOUT_PIP_SIZE 0
          description: set the ratio of the small window to 1/4"""

        return self.send(f"SET VIDOUT_PIP_SIZE {prm1}")

    def get_layout_pip_size(self):
        """description: gets the distance of the small window
        command: GET VIDOUT_PIP_SIZE
        return: VIDOOUT_PIP_SIZE prm1
        parameters:
          prm1:
            description: size
            values:
              0: 1/4
              1: 1/9
              2: 1/16
        example:
          request: GET VIDOUT_PIP_SIZE
          return: VIDOUT_PIP_SIZE 0
          description: shows the ratio of the small PiP window is 1/4"""

        return self.send("GET VIDOUT_PIP_SIZE")

    def set_osd_on(self):
        """description: turns on the OSD for 5 seconds
        command: SHOW OSD
        return: OSD 1
        example:
          request: SHOW OSD
          return: OSD 1
          description: shows OSD for 5 seconds"""

        return self.send("SHOW OSD")

    def set_cec_power(self, prm1):
        """description: sends cec power on or power off
        command: SET CEC_PWR prm1
        return: CEC_PWR prm1
        parameters:
          prm1:
            description: power status
            values:
              0: power off
              1: power on
        example:
          request: SET CEC_PWR 0
          return: CEC_PWR 0
          description: sends power off command via cec"""

        return self.send(f"SET CEC_PWR {prm1}")

    def set_cec_auto_power(self, prm1):
        """description: set cec to auto turn of/off display with hdmi in1
        command: SET AUTOCEC_FN prm1
        return: AUTOCEC_FN prm1
        parameters:
          prm1:
            description: status
            values:
              0: auto off
              1: auto on
        example:
          request: SET AUTOCEC_FN 0
          return: AUTOCEC_FN 0
          description: turns off auto cec functionality"""

        return self.send(f"SET AUTOCEC_FN {prm1}")

    def get_cec_auto_power(self):
        """description: gets auto cec power status
        command: GET AUTOCEC_FN
        return: AUTOCEC_FN prm1
        parameters:
          prm1:
            description: status
            values:
              0: auto off
              1: auto on
        example:
          request: GET AUTOCEC_FN
          return: AUTOCEC_FN 0
          description: auto cec is currently set to off"""

        return self.send("GET AUTOCEC_FN")

    def set_cec_power_delay(self, prm1):
        """description: set the time to turn off if no signal is detected in hdmi in1
        command: SET AUTOCEC_D prm1
        return: AUTOCEC_D prm1
        parameters:
          prm1:
            description: time in minutes up to 30
            values:
              1: minutes
              2: minutes Default
        example:
          request: SET AUTOCEC_D 2
          return: AUTOCEC_D 2
          description: sets auto off time to 2 minutes"""

        return self.send(f"SET AUTOCEC_D {prm1}")

    def get_cec_power_delay(self):
        """description: get auto cec power off time
        command: GET AUTOCEC_D
        return: AUTOCEC_D prm1
        parameters:
          prm1:
            description: time in minutes up to 30
            values:
              1: minutes
              2: minutes Default
        example:
          request: GET AUTOCEC_D
          return: AUTOCEC_D 2
          description: auto cec power off time is currently set to 2 minutes"""

        return self.send("GET AUTOCEC_D")

    def factory_reset(self):
        """description: unit factory resets
        command: RESET
        return: RESET
        example:
          request: RESET
          return: RESET
          description: performs a factory reset"""

        return self.send("RESET")

    def set_ir_code(self, prm1):
        """description: select between ir codes 1 or 2
        command: SET IR_SC prm1
        return: IR_SC prm1
        parameters:
          prm1:
            description: IR Set
            values:
              0: mode 1
              1: mode 2
              2: all
        example:
          request: SET IR_SC 0
          return: IR_SC 0
          description: Unit will respond to ir commands from mode1"""

        return self.send(f"SET IR_SC {prm1}")

    def get_ir_code(self):
        """description: get IR system mode
        command: GET IR_SC
        return: IR_SC prm1
        parameters:
          prm1:
            description: IR Set
            values:
              0: mode 1
              1: mode 2
              2: all
        example:
          request: GET IR_SC
          return: IR_SC 0
          description: unit is in mode1 for ir commands"""

        return self.send("GET IR_SC")

    def reboot(self):
        """description: reboot system
        command: REBOOT
        return: REBOOT
        example:
          request: REBOOT
          return: REBOOT
          description: Unit will power cycle itself"""

        return self.send("REBOOT")

    def get_input_video_info(self, prm4):
        """description: get the timing, color space, and color depth of the input
        command: GET VIDIN_INFO prm4
        return: VIDIN_INFO prm1 prm2 prm3
        parameters:
          prm1:
            description: timing
            values:
          prm2:
            description: color space
            values:
          prm3:
            description: color depth
            values:
          prm4:
            description: input
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
        example:
          request: GET VIDIN_INFO 1
          return: VIDIN_INFO 1 3840x2160@59Hz YUV422 8Bit progressive
          description: hdmi in1 is at 3840x2160@59Hz YUV422 8Bit progressive"""

        return self.send(f"GET VIDIN_INFO {prm4}")

    def get_audin_info(self, prm4):
        """description: get the audio channel details of an input
        command: GET AUDIN_INFO prm4
        return: AUDIN_INFO prm1 prm2 prm3
        parameters:
          prm1:
            description: format
            values:
          prm2:
            description: channel
            values:
          prm3:
            description: sample rate
            values:
          prm4:
            description: input
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
        example:
          request: GET AUDIN_INFO 1
          return: AUDIN_INFO 1 PCM 2ch 48Khz
          description: hdmi in1 audio is PCM 2ch 48Khz"""

        return self.send(f"GET AUDIN_INFO {prm4}")

    def get_vidout_info(self):
        """description: get the output video information
        command: GET VIDOUT_INFO
        return: VIDOUT_INFO prm1 prm2 prm3
        parameters:
          prm1:
            description: timing
            values:
          prm2:
            description: color space
            values:
          prm3:
            description: color depth
            values:
          prm4:
            description: input
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
        example:
          request: GET VIDOUT_INFO
          return: VIDOUT_INFO 3840x2160@60Hz YUV422 8Bit progressive
          description: hdmi out is at 3840x2160@60Hz YUV422 8Bit progressive"""

        return self.send("GET VIDOUT_INFO")

    def get_audout_info(self, prm4):
        """description: get the output audio information
        command: GET AUDOUT_INFO prm4
        return: AUDOUT_INFO prm4 prm1 prm2 prm3
        parameters:
          prm1:
            description: format
            values:
          prm2:
            description: channel
            values:
          prm3:
            description: sample rate
            values:
          prm4:
            description: audio out
            values:
              0: hdmi out
              1: av out
        example:
          request: GET AUDOUT_INFO 0
          return: AUDOUT_INFO 0 PCM 2ch 44.1Khz
          description: hdmi audio out is at PCM 2ch 44.1Khz"""

        return self.send(f"GET AUDOUT_INFO {prm4}")

    def get_input_valid(self, prm1):
        """description: check to see if input is valid
        command: GET VIDIN_VALID prm1
        return: VIDIN_VALID prm1 prm2
        parameters:
          prm1:
            description: input
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
          prm2:
            description: valid
            values:
              0: not valid
              1: valid
        example:
          request: GET VIDIN_VALID 1
          return: VIDIN_VALID 1 1
          description: hdmi in1 is valid"""

        return self.send(f"GET VIDIN_VAILD {prm1}")

    def get_vidout_edid(self):
        """description: read edid from display
        command: GET HDMIOUT_EDID
        return: HDMIOUT_EDID prm1
        parameters:
          prm1:
            description: 512 bytes edid ascii data with no spaces (hex data need conversion into ASCII code)
            values:
        example:
          request: GET HDMIOUT_EDID
          return: HDMIOUT_EDID XX...XX
          description: returns the EDID from HDMI out"""

        return self.send("GET HDMIOUT_EDID")

    def set_layout_original_input(self, prm1):
        """description: set the input of Original Layout mode prm1 is optional
        command: SWITCH INPUT prm1
        return: INPUT prm2 prm1
        parameters:
          prm1:
            description: input
            values:
              1: hdmi in1
              2: hdmi in2
              3: hdmi in3
              4: hdmi in4
          prm2:
            description: layout
            values:
              0: Original
        example:
          request: SWITCH INPUT 1
          return: INPUT 0 1
          description: input has switched to Original Layout and input 1"""

        if prm1:
            return self.send(f"SWITCH INPUT {prm1}")
        else:
            return self.send("SWITCH INPUT")

    def set_layout_input(self, prm1):
        """description: rotate the sources in the current or different layout mode
        command: SWITCH SOURCE prm1
        return: SOURCE prm1 prm2 prm3 prm4 prm5
        parameters:
          prm1:
            description: layout
            values:
              0: Original
              1: Dual-view
              2: PiP
              3: H
              4: Master
              5: Quad
          prm2:
            description: hdmi input
            values:
          prm3:
            description: hdmi input
            values:
          prm4:
            description: hdmi input
            values:
          prm5:
            description: hdmi input
            values:
        example:
          request: SWITCH SOURCE 0
          return: SOURCE 0 1
          description: switched to Original Layout and the next input which is 1"""

        return self.send(f"SWITCH SOURCE {prm1}")

    def switch_audout(self, prm1):
        """description: rotate the audio source
        command: SWITCH AUDOUT_WND prm1
        return: AUDOUT_WND prm1
        parameters:
          prm1:
            description: channel if left empty will rotate to the next channel 1>2>3>4>0>1
            values:
              0: mute
              1: ch 1
              2: ch 2
              3: ch 3
              4: ch 4
        example:
          request: SWITCH AUDOUT_WND
          return: AUDOUT_WND 2
          description: switched audio to channel 2"""

        if prm1:
            return self.send(f"SWITCH AUDOUT_WND {prm1}")
        else:
            return self.send("SWITCH AUDOUT_WND")

    def switch_audout_mute(self):
        """description: mute or unmute audio out
        command: SWITCH AUDOUT_MUTE
        return: AUDOUT_MUTE prm1
        parameters:
          prm1:
            description: mute status
            values:
              0: un-mute
              1: mute
        example:
          request: SWITCH AUDOUT_MUTE
          return: AUDOUT_MUTE 1
          description: all audio out is muted"""

        return self.send("SWITCH AUDOUT_MUTE")

    def power(self, prm1):
        """description: turn on, off, or toggle power
        command: POWER prm1
        return: POWER prm1
        parameters:
          prm1:
            description: power status if no parameter will toggle
            values:
              0: power off
              1: power on
        example:
          request: POWER 0
          return: POWER 0
          description: System power off"""

        return self.send(f"POWER {prm1}")

    def set_ip_mode(self, prm1):
        """description: set ip mode to dhcp, autoip, or static. requires REBOOT to take effect
        command: SET IP_MODE prm1
        return: IP_MODE prm1
        parameters:
          prm1:
            description: ip mode default is dhcp
            values:
              0: dhcp
              1: autoip
              2: static
        example:
          request: SET IP_MODE 0
          return: IP_MODE 0
          description: Set IP to DHCP must reboot to take effect."""

        return self.send(f"SET IP_MODE {prm1}")

    def get_ip_mode(self):
        """description: get ip mode: dhcp, autoip, or static.
        command: GET IP_MODE
        return: IP_MODE prm1
        parameters:
          prm1:
            description: ip mode default is dhcp
            values:
              0: dhcp
              1: autoip
              2: static
        example:
          request: GET IP_MODE
          return: IP_MODE 0
          description: IP is currently HDCP"""

        return self.send("GET IP_MODE")

    def set_ip(self, prm1, prm2, prm3):
        """description: set ip address
        command: SET IPADDR prm1 prm2 prm3
        return: IPADDR prm1 prm2 prm3
        parameters:
          prm1:
            description: ip address
            values:
          prm2:
            description: subnet mask
            values:
          prm3:
            description: gateway
            values:
        example:
          request: SET IPADDR 192.168.1.4 255.255.255.0 192.168.1.1
          return: IPADDR 192.168.1.4 255.255.255.0 192.168.1.1
          description: Set the ip address, subnet, and gateway"""

        return self.send(f"SET IPADDR {prm1} {prm2} {prm3}")

    def get_ip(self) -> Dict[str, str]:
        """Get the IP configuration of the device.

        Returns:
            Dict[str, str]: Dictionary containing ip, subnet, and gateway
        """
        return self.send("GET IPADDR")

    def get_mac(self) -> Dict[str, str]:
        """Get the MAC address of the device.

        Returns:
            Dict[str, str]: Dictionary containing MAC address
        """
        return self.send("GET MAC")

    def set_osd(self, prm1):
        """description: turn OSD on or off
        command: SET OSD prm1
        return: OSD prm1
        parameters:
          prm1:
            description: power on or off
            values:
              0: turn off osd
              1: turn on osd
        example:
          request: SET OSD 1
          return: OSD 1
          description: Turn OSD on"""

        return self.send(f"SET OSD {prm1}")

    def get_osd(self) -> Dict[str, bool]:
        """Get the current OSD status.

        Returns:
            Dict[str, bool]: Dictionary containing OSD status
        """
        return self.send("GET OSD")

    def set_osd_time(self, prm1):
        """description: set how long the osd will stay on
        command: SET OSD_T prm1
        return: OSD_T prm1
        parameters:
          prm1:
            description: seconds 3-10s 5s is default
            values:
        example:
          request: SET OSD_T 3
          return: OSD_T 3
          description: Sets OSD display time to 3 seconds"""

        return self.send(f"SET OSD_T {prm1}")

    def get_osd_time(self) -> Dict[str, int]:
        """Get the current OSD timeout.

        Returns:
            Dict[str, int]: Dictionary containing OSD timeout
        """
        return self.send("GET OSD_T")

    def set_vidout_colorimetry(self, prm1):
        """description: set the video output colorimetry
        command: SET VIDOUT_CR prm1
        return: VIDOUT_CR prm1
        parameters:
          prm1:
            description: Colorimetry setting
            values:
              0: Follow source (default)
              1: Follow sink
              2: Fixed BT.2020
              3: Fixed BT.709
              4: Fixed BT.601
        example:
          request: SET VIDOUT_CR 1
          return: VIDOUT_CR 1
          description: Colorimetry is set to follow sink"""

        return self.send(f"SET VIDOUT_CR {prm1}")

    def get_vidout_colorimetry(self):
        """description: get the video output colorimetry
        command: GET VIDOUT_CR
        return: VIDOUT_CR prm1
        parameters:
          prm1:
            description: Colorimetry setting
            values:
              0: Follow source (default)
              1: Follow sink
              2: Fixed BT.2020
              3: Fixed BT.709
              4: Fixed BT.601
        example:
          request: GET VIDOUT_CR
          return: VIDOUT_CR 1
          description: Colorimetry is set to follow sink"""

        return self.send("GET VIDOUT_CR")


if __name__ == "__main__":
    mv = MV0401_Device("10.0.110.204")
    print(mv.get_ip())
    print(mv.get_version())
