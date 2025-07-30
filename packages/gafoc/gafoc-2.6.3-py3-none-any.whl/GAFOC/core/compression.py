# GAFOC/core/compression.py
# Implements the Smart Threshold logic.

import lz4.frame
import zstandard as zstd
import zlib
import brotli
from .huffman import HuffmanEncoder
from ..exceptions import CompressionError

# A special, unique header to signify that Huffman was skipped.
# Format: A magic sequence that's highly unlikely to appear naturally.
HUFFMAN_SKIPPED_MAGIC = b'__!HFSKIP!__'

class GAFOCompressor:
    """
    A smart hybrid compressor. It always uses a base compressor (like LZ4),
    and then intelligently decides whether applying Huffman coding is worthwhile.
    """
    def __init__(self, compression_level: int = 5):
        self.huffman_encoder = HuffmanEncoder()

        # We now define multiple "base" compressors.
        # The 'smart' choice will be which of these to use as a base.
        # For simplicity in this implementation, we will stick to LZ4 as the base.
        # The adaptive choice logic can be added on top later.
        
        self.base_compressor = lambda data: lz4.frame.compress(data, compression_level=compression_level)
        self.base_compressor_name = "lz4"

    def compress_data(self, data: bytes) -> bytes:
        """
        Compresses data using a base algorithm, then applies Huffman only if it's
        beneficial. If Huffman is skipped, a special header is prepended.
        """
        if not data:
            return b''
        
        data_len = len(data)

        # Stage 1: Always compress with the base algorithm (fast LZ4)
        base_compressed = self.base_compressor(data)
        base_len = len(base_compressed)

        # --- SMART THRESHOLD DECISION ---
        # If the base compression was ineffective (didn't reduce size by at least 1%),
        # applying Huffman is likely a waste of CPU time and will add header overhead.
        if base_len >= data_len * 0.99:
            # Mark this data chunk as "Huffman-skipped"
            return HUFFMAN_SKIPPED_MAGIC + base_compressed

        # Stage 2: If base compression was good, try applying Huffman.
        huffman_compressed = self.huffman_encoder.encode(base_compressed)
        huffman_len = len(huffman_compressed)

        # --- FINAL CHECK ---
        # Did Huffman actually make it smaller? Or did its header add too much overhead?
        if huffman_len >= base_len:
            # Huffman was not beneficial. Use the base result, but mark it as skipped.
            return HUFFMAN_SKIPPED_MAGIC + base_compressed
        else:
            # Success! The full hybrid compression was the best.
            # No special header is needed, its absence implies Huffman was used.
            return huffman_compressed