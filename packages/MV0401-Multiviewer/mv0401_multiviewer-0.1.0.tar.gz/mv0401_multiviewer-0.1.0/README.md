# MV0401 Python Telnet Wrapper

A Python wrapper for controlling the MV0401 device via Telnet. This package provides a simple interface to send commands and receive structured responses from the device.

## Installation

You can install the package from PyPI using pip:

```bash
pip install mv0401
```

## Usage

Here's a quick example of how to use the package:

```python
from mv0401 import MV0401_Device

# Create a device instance
device = MV0401_Device("10.0.110.204")

# Connect to the device
device.connect()

# Get the IP configuration
ip_config = device.get_ip()
print(ip_config)

# Get the firmware version
version = device.get_version()
print(version)

# Disconnect from the device
device.disconnect()
```

## Features

- Structured response parsing for all device commands
- Human-readable output for video and audio information
- Support for all device commands (GET/SET)

## Links

- [GitHub Repository](https://github.com/yourusername/mv0401)
- [PyPI Package](https://pypi.org/project/mv0401/)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
