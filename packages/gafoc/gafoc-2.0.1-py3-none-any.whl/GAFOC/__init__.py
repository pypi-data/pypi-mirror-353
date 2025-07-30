from .core import GAFOCompressor, GAFODecompressor
from .archive import GAFOArchiver, GAFOExtractor
from .exceptions import (GAFOError, CompressionError, 
                        DecompressionError, ArchiveError, ExtractionError)

__version__ = "0.3.0"
__all__ = [
    'GAFOCompressor',
    'GAFODecompressor',
    'GAFOArchiver',
    'GAFOExtractor',
    'GAFOError',
    'CompressionError',
    'DecompressionError',
    'ArchiveError',
    'ExtractionError'
]