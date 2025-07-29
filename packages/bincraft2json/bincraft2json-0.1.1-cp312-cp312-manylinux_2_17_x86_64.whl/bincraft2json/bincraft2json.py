from ._core import decode_bincraft, decode_bincraft_buffer

def convert_bincraft_to_json(filename, zstd_compressed=False):
    """
    Convertit un fichier BinCraft en JSON.
    
    Args:
        filename (str): Chemin vers le fichier BinCraft
        zstd_compressed (bool): Indique si le fichier est compressé avec zstd
        
    Returns:
        dict: Les données de l'aéronef au format JSON
    """
    return decode_bincraft(filename, zstd_compressed)

def convert_bincraft_buffer_to_json(buffer, zstd_compressed=False):
    """
    Convertit un buffer BinCraft en JSON.
    
    Args:
        buffer (bytes): Buffer contenant les données BinCraft
        zstd_compressed (bool): Indique si les données sont compressées avec zstd
        
    Returns:
        dict: Les données de l'aéronef au format JSON
    """
    return decode_bincraft_buffer(buffer, zstd_compressed) 