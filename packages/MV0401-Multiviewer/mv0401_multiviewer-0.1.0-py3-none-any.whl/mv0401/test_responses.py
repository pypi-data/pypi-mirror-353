from mv0401 import MV0401_Device
from pprint import pprint


def print_response(title: str, response: dict):
    """Print a response with a title in a readable format"""
    print(f"\n{'=' * 50}")
    print(f"{title}")
    print(f"{'=' * 50}")
    pprint(response)
    print(f"{'=' * 50}\n")


def main():
    # Connect to device
    device = MV0401_Device("10.0.110.204")
    if not device.connect():
        print("Failed to connect to device")
        return

    try:
        # Test all GET commands
        print_response("IP Configuration", device.get_ip())
        print_response("Firmware Version", device.get_version())
        print_response("MAC Address", device.get_mac())
        print_response("Current Layout", device.get_layout())
        print_response("Video Resolution", device.get_vid_res())
        print_response("Audio Output Channel", device.get_audout_chan())
        print_response("Audio Output Window", device.get_audout_window())
        print_response("OSD Status", device.get_osd())
        print_response("OSD Timeout", device.get_osd_time())

        # Test input-related commands
        for input_num in range(1, 5):
            print_response(
                f"Input {input_num} Validity", device.get_input_valid(input_num)
            )
            print_response(
                f"Input {input_num} Video Info", device.get_input_video_info(input_num)
            )
            print_response(
                f"Input {input_num} Audio Info", device.get_audin_info(input_num)
            )

        # Test output-related commands
        print_response("Video Output Info", device.get_vidout_info())
        for output_num in [0, 1]:  # 0: HDMI out, 1: AV out
            print_response(
                f"Audio Output {output_num} Info", device.get_audout_info(output_num)
            )

    finally:
        device.disconnect()


if __name__ == "__main__":
    main()
