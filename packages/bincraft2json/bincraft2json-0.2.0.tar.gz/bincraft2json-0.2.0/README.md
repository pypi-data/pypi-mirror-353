# BinCraft2JSON

[![PyPI version](https://badge.fury.io/py/bincraft2json.svg)](https://badge.fury.io/py/bincraft2json)
[![Python versions](https://img.shields.io/pypi/pyversions/bincraft2json.svg)](https://pypi.org/project/bincraft2json/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python module to decode BinCraft files (optionally ZSTD-compressed) and convert aircraft data to JSON.

BinCraft is a binary format used for storing aircraft tracking data efficiently. This module provides a fast C++ implementation with Python bindings to decode these files into easily usable JSON format.

## Features

- **Fast C++ implementation** with Python bindings using pybind11
- **ZSTD compression support** for compressed BinCraft files
- **Multiple input types**: file paths, pathlib.Path objects, or raw bytes
- **Memory efficient** processing of large datasets
- **Cross-platform** support (Linux, macOS, Windows)

## Installation

### From PyPI (recommended)

```bash
pip install bincraft2json
```

### System Requirements

- Python 3.7+
- libzstd (automatically handled on most systems)

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get install libzstd-dev
```

#### macOS
```bash
brew install zstd
```

#### Windows
ZSTD is automatically linked on Windows through the wheel distribution.

## Quick Start

### Decode a file

```python
import bincraft2json

# Decode a ZSTD-compressed BinCraft file
data = bincraft2json.decode_bincraft("flight_data.bin", zstd_compressed=True)

# Decode an uncompressed BinCraft file
data = bincraft2json.decode_bincraft("flight_data.bin", zstd_compressed=False)

# Process the results
for aircraft in data:
    print(f"Aircraft {aircraft['hex']}: lat={aircraft['lat']}, lon={aircraft['lon']}")
```

### Decode HTTP response data

```python
import bincraft2json
import httpx

# Fetch data from an API
response = httpx.get("https://api.example.com/bincraft-data", headers=headers)

# Decode the binary response
data = bincraft2json.decode_bincraft(response.content, zstd_compressed=True)

for aircraft in data:
    print(f"Flight {aircraft['flight']}: {aircraft['lat']}, {aircraft['lon']}")
```

### With requests

```python
import bincraft2json
import requests

response = requests.get("https://api.example.com/bincraft-data", headers=headers)
data = bincraft2json.decode_bincraft(response.content, zstd_compressed=True)
```

## Data Structure

Each aircraft in the returned list contains comprehensive flight data:

```python
{
    "hex": "abc123",              # Aircraft identifier (hex)
    "lat": 48.8566,              # Latitude
    "lon": 2.3522,               # Longitude
    "alt_baro": 35000,           # Barometric altitude (feet)
    "alt_geom": 35025,           # Geometric altitude (feet)
    "gs": 450.5,                 # Ground speed (knots)
    "track": 180.0,              # Track angle (degrees)
    "flight": "AF1234",          # Flight number
    "squawk": "1234",            # Transponder code
    "category": "A3",            # Aircraft category
    "type": "adsb_icao",         # Message type
    "seen": 0.5,                 # Time since last seen (seconds)
    "seen_pos": 1.2,             # Time since last position (seconds)
    "nav_modes": ["autopilot"],  # Navigation modes
    "baro_rate": 0,              # Barometric rate of climb (ft/min)
    "geom_rate": 64,             # Geometric rate of climb (ft/min)
    "nav_altitude_mcp": 35000,   # MCP selected altitude
    "nav_altitude_fms": 35000,   # FMS selected altitude
    "nav_qnh": 1013.25,          # QNH setting
    "nav_heading": 180.0,        # Selected heading
    "mach": 0.78,                # Mach number
    "roll": -2.5,                # Roll angle (degrees)
    "track_rate": 0.2,           # Rate of turn (degrees/second)
    "mag_heading": 179.5,        # Magnetic heading
    "true_heading": 180.5,       # True heading
    "wd": 270,                   # Wind direction (degrees)
    "ws": 45,                    # Wind speed (knots)
    "oat": -48,                  # Outside air temperature (°C)
    "tat": -32,                  # Total air temperature (°C)
    "tas": 475,                  # True airspeed (knots)
    "ias": 320,                  # Indicated airspeed (knots)
    "rc": 256,                   # Reply capability
    "messages": 1247,            # Message count
    "nic": 8,                    # Navigation integrity category
    "emergency": 0,              # Emergency status
    "airground": 0,              # Air/ground status
    "nav_altitude_src": 0,       # Altitude source
    "sil_type": 3,               # Source integrity level type
    "adsb_version": 2,           # ADS-B version
    "adsr_version": 0,           # ADS-R version
    "tisb_version": 0,           # TIS-B version
    "nac_p": 9,                  # Navigation accuracy category - position
    "nac_v": 2,                  # Navigation accuracy category - velocity
    "sil": 3,                    # Source integrity level
    "gva": 2,                    # Geometric vertical accuracy
    "sda": 2,                    # System design assurance
    "nic_a": 0,                  # Navigation integrity category - A
    "nic_c": 0,                  # Navigation integrity category - C
    "nic_baro": 1,               # Navigation integrity category - barometric
    "alert": 0,                  # Alert flag
    "spi": 0,                    # Special position identification
    "rssi": -23.5,               # Received signal strength indicator
    "dbFlags": 0,                # Database flags
    "t": "adsb",                 # Type
    "r": "EGLL",                 # Receiver
    "receiverCount": 3           # Number of receivers
}
```

## Error Handling

The module raises appropriate Python exceptions:

```python
try:
    data = bincraft2json.decode_bincraft("nonexistent.bin", True)
except FileNotFoundError:
    print("File not found")
except RuntimeError as e:
    print(f"Decoding error: {e}")
except TypeError:
    print("Unsupported source type")
```

## Supported Input Types

The `decode_bincraft` function accepts:

- `str`: File path
- `pathlib.Path`: Path object
- `bytes`: Raw binary data in memory

## Performance

This module is optimized for performance:

- **C++ implementation** for fast binary parsing
- **Zero-copy operations** where possible
- **Efficient memory usage** for large files
- **SIMD optimizations** in the underlying C++ code

## Development

### Building from source

```bash
# Clone the repository
git clone https://github.com/aymene69/bincraft2json.git
cd bincraft2json

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```

### Requirements for building

- C++17 compatible compiler
- CMake (for building dependencies)
- libzstd development headers

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Created by [@aymene69](https://github.com/aymene69)

## Related Projects

- [BinCraft](https://github.com/aymene69/bincraft) - Original BinCraft format specification
- [nlohmann/json](https://github.com/nlohmann/json) - JSON library used internally
