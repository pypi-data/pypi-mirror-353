# GAFOC/core/decompression.py
# Updated to handle the Smart Threshold logic.

import traceback
from ..exceptions import DecompressionError
from .huffman import HuffmanDecoder
import lz4.frame

# Must be the exact same magic sequence as in the compressor.
HUFFMAN_SKIPPED_MAGIC = b'__!HFSKIP!__'

class GAFODecompressor:
    """
    Decompresses data by first checking if Huffman was skipped.
    """
    def __init__(self):
        self.huffman_decoder = HuffmanDecoder()
        # The base decompressor (must match the one in GAFOCompressor)
        self.base_decompressor = lz4.frame.decompress

    def decompress_data(self, data_chunk: bytes) -> bytes:
        """
        The core decompression function. It checks for the magic header
        to decide whether to run Huffman decompression or not.
        """
        if not data_chunk:
            return b''

        try:
            # --- SMART THRESHOLD DECODING ---
            # Check if the data chunk starts with our special "skipped" marker.
            if data_chunk.startswith(HUFFMAN_SKIPPED_MAGIC):
                # If yes, Huffman was skipped. The rest of the data is raw base-compressed data.
                base_compressed = data_chunk[len(HUFFMAN_SKIPPED_MAGIC):]
            else:
                # Otherwise, it's a standard hybrid chunk. Apply Huffman decompression.
                base_compressed = self.huffman_decoder.decode(data_chunk)
            
            # Stage 2: Always decompress the base algorithm to get the original data.
            original_data = self.base_decompressor(base_compressed)
            
            return original_data
            
        except Exception as e:
            print("\n" + "="*80)
            print(">>> DEBUG: Error in GAFODecompressor <<<")
            traceback.print_exc()
            print("="*80 + "\n")
            raise DecompressionError(f"Decompression failed: {str(e)}") from e