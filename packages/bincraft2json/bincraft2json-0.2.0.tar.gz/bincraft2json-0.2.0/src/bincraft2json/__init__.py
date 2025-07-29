"""
Python module to decode BinCraft files to JSON

Usage:
    import bincraft2json
    
    # Decode a file
    data = bincraft2json.decode_bincraft("path/to/file.bin", zstd_compressed=True/False)
    
    # Decode data in memory
    response = httpx.get(url, headers=headers)
    data = bincraft2json.decode_bincraft(response.content, zstd_compressed=True/False)
"""

import json
from typing import Union, List, Dict, Any
from pathlib import Path

try:
    from ._core import decode_bincraft_file, decode_bincraft_bytes
except ImportError as e:
    raise ImportError(
        "C++ module not compiled. Please install the module with pip install ."
    ) from e


def decode_bincraft(
    source: Union[str, Path, bytes], 
    zstd_compressed: bool = False
) -> List[Dict[str, Any]]:
    """
    Decode a BinCraft file or binary data to JSON.
    
    Args:
        source: Path to BinCraft file or binary data
        zstd_compressed: True if data is compressed with ZSTD
        
    Returns:
        List of decoded aircraft as Python dictionaries
        
    Raises:
        TypeError: If source type is not supported
        RuntimeError: If decoding fails
        
    Examples:
        >>> # Decode a file
        >>> data = decode_bincraft("flight_data.bin", zstd_compressed=True)
        >>> 
        >>> # Decode HTTP data
        >>> import httpx
        >>> response = httpx.get(url, headers=headers)
        >>> data = decode_bincraft(response.content, zstd_compressed=True)
    """
    if isinstance(source, (str, Path)):
        # Source is a file path
        file_path = str(source)
        json_result = decode_bincraft_file(file_path, zstd_compressed)
    elif isinstance(source, bytes):
        # Source is binary data
        json_result = decode_bincraft_bytes(source, zstd_compressed)
    else:
        raise TypeError(
            f"Source type '{type(source)}' is not supported. "
            "Use str, Path or bytes."
        )
    
    # Convert JSON string to Python object
    return json.loads(json_result)


__version__ = "0.2.0"
__all__ = ["decode_bincraft"] 