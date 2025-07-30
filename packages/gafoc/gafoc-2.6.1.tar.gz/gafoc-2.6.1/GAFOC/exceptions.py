class GAFOError(Exception):
    """Base exception for GAFO library"""
    pass

class CompressionError(GAFOError):
    """Error during compression"""
    pass

class DecompressionError(GAFOError):
    """Error during decompression"""
    pass

class ArchiveError(GAFOError):
    """Error during archive creation"""
    pass

class ExtractionError(GAFOError):
    """Error during archive extraction"""
    pass