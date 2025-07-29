#!/usr/bin/env python3
"""
Usage example for bincraft2json module

Author: @aymene69
License: MIT
"""

import bincraft2json
import sys


def example_file():
    """Example of decoding a file"""
    if len(sys.argv) < 2:
        print("Usage: python example.py <file.bin> [zstd_compressed]")
        return
    
    filename = sys.argv[1]
    zstd_compressed = len(sys.argv) > 2 and sys.argv[2].lower() in ['true', '1', 'yes']
    
    try:
        print(f"Decoding file: {filename}")
        print(f"ZSTD compressed: {zstd_compressed}")
        
        data = bincraft2json.decode_bincraft(filename, zstd_compressed)
        
        print(f"Number of aircraft found: {len(data)}")
        
        for i, aircraft in enumerate(data[:5]):  # Show first 5
            print(f"\nAircraft {i+1}:")
            print(f"  Hex: {aircraft.get('hex', 'N/A')}")
            print(f"  Position: {aircraft.get('lat', 'N/A')}, {aircraft.get('lon', 'N/A')}")
            print(f"  Altitude: {aircraft.get('alt_baro', 'N/A')} ft")
            print(f"  Ground speed: {aircraft.get('gs', 'N/A')} kt")
            print(f"  Flight: {aircraft.get('flight', 'N/A')}")
            print(f"  Type: {aircraft.get('type', 'N/A')}")
        
        if len(data) > 5:
            print(f"\n... and {len(data) - 5} other aircraft")
            
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
    except RuntimeError as e:
        print(f"Decoding error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def example_bytes():
    """Example of decoding data in memory"""
    
    # Create minimal example data
    print("Example with in-memory data:")
    
    # Minimal header (20 bytes with stride=105)
    header = bytearray(20)
    header[8:12] = (105).to_bytes(4, 'little')  # stride
    
    try:
        data = bincraft2json.decode_bincraft(bytes(header), False)
        print(f"Decoded data (empty): {len(data)} aircraft")
    except RuntimeError as e:
        print(f"Expected error with minimal data: {e}")


def example_http_simulation():
    """Simulated example of decoding HTTP data"""
    
    print("\nSimulated HTTP data example:")
    
    # Simulate response.content
    class MockResponse:
        def __init__(self, content):
            self.content = content
    
    # Create minimal header
    header = bytearray(20)
    header[8:12] = (105).to_bytes(4, 'little')
    
    mock_response = MockResponse(bytes(header))
    
    try:
        data = bincraft2json.decode_bincraft(mock_response.content, False)
        print(f"HTTP data decoded: {len(data)} aircraft")
    except RuntimeError as e:
        print(f"Error with simulated data: {e}")


if __name__ == "__main__":
    print("=== bincraft2json Example ===")
    print(f"Module version: {bincraft2json.__version__}")
    print()
    
    if len(sys.argv) > 1:
        example_file()
    else:
        print("No file specified, running basic examples:")
        example_bytes()
        example_http_simulation()
        print()
        print("To decode a file:")
        print("python example.py <file.bin> [true|false]") 