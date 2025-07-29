"""
Tests for bincraft2json module
"""

import pytest
import tempfile
import os
from pathlib import Path

try:
    import bincraft2json
except ImportError:
    pytest.skip("bincraft2json module not compiled", allow_module_level=True)


def test_decode_bincraft_types():
    """Test that the function accepts the right types"""
    
    # Test with string
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        # Create minimal file (empty for this test)
        tmp.write(b'\x00' * 100)
        tmp.flush()
        
        try:
            # Should raise RuntimeError for insufficient data
            with pytest.raises(RuntimeError):
                bincraft2json.decode_bincraft(tmp.name, False)
        finally:
            os.unlink(tmp.name)
    
    # Test with Path
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b'\x00' * 100)
        tmp.flush()
        
        try:
            path = Path(tmp.name)
            with pytest.raises(RuntimeError):
                bincraft2json.decode_bincraft(path, False)
        finally:
            os.unlink(tmp.name)
    
    # Test with bytes
    data = b'\x00' * 100
    with pytest.raises(RuntimeError):
        bincraft2json.decode_bincraft(data, False)
    
    # Test with invalid type
    with pytest.raises(TypeError):
        bincraft2json.decode_bincraft(123, False)


def test_decode_bincraft_empty_data():
    """Test with empty data"""
    
    # Data too short
    with pytest.raises(RuntimeError, match="Insufficient"):
        bincraft2json.decode_bincraft(b'\x00' * 10, False)


def test_decode_bincraft_minimal_valid():
    """Test with minimal valid data"""
    
    # Create minimal header with stride
    header = bytearray(20)
    # Set stride of 20 at offset 8
    header[8:12] = (20).to_bytes(4, 'little')
    
    # No aircraft, just header
    result = bincraft2json.decode_bincraft(bytes(header), False)
    assert result == []


def test_module_attributes():
    """Test that module has expected attributes"""
    
    assert hasattr(bincraft2json, 'decode_bincraft')
    assert hasattr(bincraft2json, '__version__')
    assert bincraft2json.__version__ == "0.2.0" 