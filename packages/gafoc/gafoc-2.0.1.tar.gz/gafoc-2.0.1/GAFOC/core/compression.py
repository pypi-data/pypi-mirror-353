# GAFOC/core/compression.py

import os
import struct
from ..exceptions import CompressionError
from .huffman import HuffmanEncoder # Huffman is still useful on top of LZ4
import lz4.frame # Using the robust LZ4 library

class GAFOCompressor:
    """
    Compresses data using a two-stage process: LZ4 for speed and initial reduction,
    followed by Huffman coding to compress the LZ4 output pattern.
    """
    def __init__(self, compression_level: int = 4):
        """
        Initializes the compressor.
        Args:
            compression_level: An integer from 0 to 16 for LZ4.
                               A good default is 4 (fast with good ratio).
                               9 is similar to zlib's default. 16 is for high compression.
        """
        # We adapt the level for LZ4's scale. 0-16.
        if not 0 <= compression_level <= 16:
            raise ValueError("Compression level for LZ4 mode must be between 0 and 16.")
            
        self.compression_level = compression_level
        self.huffman_encoder = HuffmanEncoder()

    def compress_data(self, data: bytes) -> bytes:
        """
        Compresses raw data using LZ4 and then Huffman coding.
        """
        if not data:
            return b''
            
        try:
            # Stage 1: Compress with LZ4 - fast and effective
            lz4_compressed = lz4.frame.compress(data, compression_level=self.compression_level)
            
            # Stage 2: Compress the LZ4 output with Huffman. This can further
            # reduce the size if the LZ4 output has a biased byte distribution.
            final_compressed = self.huffman_encoder.encode(lz4_compressed)
            
            return final_compressed
        except Exception as e:
            raise CompressionError(f"Data compression failed: {e}") from e

    def compress_file(self, input_path: str, output_path: str) -> None:
        """
        Compresses a single file into a GAFO standalone file.
        This is not for archives, but for single file compression.
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
            
        try:
            with open(input_path, 'rb') as f_in:
                data = f_in.read()
                
            compressed = self.compress_data(data)
            
            with open(output_path, 'wb') as f_out:
                # GAFO Standalone File Header
                f_out.write(b'GAFO') 
                f_out.write(struct.pack('>B', self.compression_level)) # Store the level
                f_out.write(struct.pack('>Q', len(data))) # Store original size
                f_out.write(compressed)
                
        except IOError as e:
            raise CompressionError(f"File operation failed: {str(e)}") from e