import struct
from typing import Tuple
from ..exceptions import DecompressionError
from .lz77 import LZ77Decompressor
from .huffman import HuffmanDecoder

class GAFODecompressor:
    def __init__(self):
        self.lz77 = LZ77Decompressor()
        self.huffman = HuffmanDecoder()

    def decompress_data(self, compressed_data: bytes) -> Tuple[bytes, int]:
        """Decompress GAFO compressed data"""
        try:
            if len(compressed_data) < 13 or not compressed_data.startswith(b'GAFO'):
                raise DecompressionError("Invalid GAFO format")
                
            compression_level = compressed_data[4]
            original_size = struct.unpack('>Q', compressed_data[5:13])[0]
            huffman_encoded = compressed_data[13:]
            
            lz77_compressed = self.huffman.decode(huffman_encoded)
            decompressed = self.lz77.decompress(lz77_compressed)
            
            if len(decompressed) != original_size:
                raise DecompressionError("Decompressed size mismatch")
                
            return decompressed, compression_level
            
        except Exception as e:
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