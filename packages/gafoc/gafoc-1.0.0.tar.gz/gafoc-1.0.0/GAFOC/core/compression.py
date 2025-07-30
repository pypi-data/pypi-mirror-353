import os
import struct
from typing import Tuple, Dict
from collections import defaultdict
import heapq
from ..exceptions import CompressionError
from .lz77 import LZ77Compressor
from .huffman import HuffmanEncoder

class GAFOCompressor:
    def __init__(self, compression_level: int = 6):
        """
        Initialize GAFO compressor with compression level (1-9)
        
        Args:
            compression_level: Level of compression (1-9), higher means better compression but slower
        """
        if not 1 <= compression_level <= 9:
            raise ValueError("Compression level must be between 1 and 9")
            
        self.compression_level = compression_level
        self.lz77 = LZ77Compressor(compression_level)
        self.huffman = HuffmanEncoder()

    def compress_data(self, data: bytes) -> bytes:
        """Compress raw data using LZ77 + Huffman coding"""
        try:
            lz77_compressed = self.lz77.compress(data)
            return self.huffman.encode(lz77_compressed)
        except Exception as e:
            raise CompressionError(f"Data compression failed: {str(e)}") from e

    def compress_file(self, input_path: str, output_path: str) -> None:
        """Compress single file to GAFO format"""
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
            
        try:
            with open(input_path, 'rb') as f_in:
                data = f_in.read()
                
            compressed = self.compress_data(data)
            
            with open(output_path, 'wb') as f_out:
                # Write GAFO header
                f_out.write(b'GAFO')
                f_out.write(struct.pack('>B', self.compression_level))
                f_out.write(struct.pack('>Q', len(data)))  # Original size
                f_out.write(compressed)
                
        except IOError as e:
            raise CompressionError(f"File operation failed: {str(e)}") from e