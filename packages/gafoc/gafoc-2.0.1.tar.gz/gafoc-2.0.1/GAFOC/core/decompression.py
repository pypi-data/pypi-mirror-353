# GAFOC/core/decompression.py

import struct
import traceback
from ..exceptions import DecompressionError
from .huffman import HuffmanDecoder # We still need to decode Huffman first
import lz4.frame # Using the robust LZ4 library

class GAFODecompressor:
    """
    Decompresses data compressed by GAFOCompressor by reversing the process:
    Huffman Decode -> LZ4 Decompress.
    """
    def __init__(self):
        self.huffman_decoder = HuffmanDecoder()

    def decompress_chunk(self, data_chunk: bytes) -> bytes:
        """
        The core function used by the GAFOExtractor to decompress a data chunk from an archive.
        """
        if not data_chunk:
            return b''

        try:
            # Stage 1: Undo Huffman encoding to get the LZ4 compressed stream
            lz4_compressed = self.huffman_decoder.decode(data_chunk)
            
            # Stage 2: Undo LZ4 compression to get the original data
            original_data = lz4.frame.decompress(lz4_compressed)
            
            return original_data
        except Exception as e:
            print("\n" + "="*80)
            print(">>> DEBUG: An error occurred inside GAFODecompressor.decompress_chunk <<<")
            print("This is the original, detailed error traceback:")
            traceback.print_exc()
            print("="*80 + "\n")
            raise DecompressionError(f"Raw chunk decompression failed: {str(e)}") from e

    def decompress_file(self, input_path: str, output_path: str):
        """
        Decompresses a single GAFO-compressed file from disk.
        """
        try:
            with open(input_path, 'rb') as f_in:
                full_content = f_in.read()

            if len(full_content) < 13 or not full_content.startswith(b'GAFO'):
                raise DecompressionError("Invalid standalone GAFO format.")

            level = full_content[4]
            original_size = struct.unpack('>Q', full_content[5:13])[0]
            data_chunk = full_content[13:]
            
            decompressed_data = self.decompress_chunk(data_chunk)
            
            if len(decompressed_data) != original_size:
                raise DecompressionError("Decompressed data size does not match original size.")

            with open(output_path, 'wb') as f_out:
                f_out.write(decompressed_data)
        
        except (IOError, DecompressionError) as e:
            raise DecompressionError(f"File decompression failed: {e}") from e