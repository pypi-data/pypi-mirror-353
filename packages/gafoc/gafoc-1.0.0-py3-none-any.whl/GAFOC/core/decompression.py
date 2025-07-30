# decompression.py

import struct
from typing import Tuple
from ..exceptions import DecompressionError
from .lz77 import LZ77Decompressor
from .huffman import HuffmanDecoder

class GAFODecompressor:
    def __init__(self):
        self.lz77 = LZ77Decompressor()
        self.huffman = HuffmanDecoder()

    def decompress_chunk(self, data_chunk: bytes) -> bytes:
        """
        Decompresses a raw data chunk (Huffman -> LZ77) without a GAFO header.
        This is used by the extractor.
        """
        try:
            lz77_compressed = self.huffman.decode(data_chunk)
            decompressed = self.lz77.decompress(lz77_compressed)
            return decompressed
        except Exception as e:
            raise DecompressionError(f"Raw chunk decompression failed: {str(e)}") from e

    def decompress_data(self, compressed_data: bytes) -> Tuple[bytes, int]:
        """
        Decompress a full GAFO-formatted data stream (with header).
        This is for standalone file decompression.
        """
        try:
            if len(compressed_data) < 13 or not compressed_data.startswith(b'GAFO'):
                raise DecompressionError("Invalid GAFO format (magic number 'GAFO' not found)")
                
            compression_level = compressed_data[4]
            original_size = struct.unpack('>Q', compressed_data[5:13])[0]
            
            # The actual compressed chunk starts after the header
            huffman_encoded_chunk = compressed_data[13:]
            
            # Use the new chunk decompression method for the core logic
            decompressed = self.decompress_chunk(huffman_encoded_chunk)
            
            if len(decompressed) != original_size:
                raise DecompressionError(f"Decompressed size mismatch. Expected {original_size}, got {len(decompressed)}")
                
            return decompressed, compression_level
            
        except Exception as e:
            # Avoid re-wrapping the same error message
            if isinstance(e, DecompressionError):
                raise
            raise DecompressionError(f"Data decompression failed: {str(e)}") from e

    def decompress_file(self, input_path: str, output_path: str) -> int:
        """Decompress GAFO file"""
        try:
            with open(input_path, 'rb') as f_in:
                compressed_data = f_in.read()
                
            decompressed, compression_level = self.decompress_data(compressed_data)
            
            with open(output_path, 'wb') as f_out:
                f_out.write(decompressed)
                
            return compression_level
            
        except IOError as e:
            raise DecompressionError(f"File operation failed: {str(e)}") from e