# lz77.py

from typing import List, Tuple
from collections import defaultdict

class LZ77Compressor:
    def __init__(self, compression_level: int):
        # 11 bits for offset -> max 2047. 4 bits for length -> max 15.
        self.window_size = 2048
        self.lookahead_buffer = 15 + 3 # 4 bits for length (0-15) + min_match
        self.min_match_length = 3

    def compress(self, data: bytes) -> bytes:
        """LZ77 compression with improved search using hash table"""
        compressed = bytearray()
        pos = 0
        len_data = len(data)
        
        # Using a simple list as a hash table for simplicity and correctness
        hash_table = defaultdict(list)
        
        # Pre-fill hash table for the first few bytes
        if len_data >= self.min_match_length:
            for i in range(len_data - self.min_match_length + 1):
                h = self._hash_data(data, i, self.min_match_length)
                hash_table[h].append(i)

        while pos < len_data:
            best_offset, best_length = 0, 0
            
            # Find the best match
            if pos + self.min_match_length <= len_data:
                current_hash = self._hash_data(data, pos, self.min_match_length)
                for candidate in reversed(hash_table.get(current_hash, [])):
                    # Ensure candidate is within the sliding window and before current position
                    if candidate >= pos:
                        continue
                    if pos - candidate >= self.window_size:
                        break # Candidates are sorted, so we can stop

                    length = self._match_length(data, candidate, pos, len_data)
                    
                    if length > best_length:
                        best_length = length
                        best_offset = pos - candidate
                        # Optimization: if we have the best possible match, stop searching
                        if best_length >= self.lookahead_buffer:
                            break
            
            if best_length >= self.min_match_length:
                compressed.extend(self._encode_token(best_offset, best_length))
                pos += best_length
            else:
                # Literal: flag byte 0x80 followed by the actual byte
                compressed.append(0x80)
                compressed.append(data[pos])
                pos += 1
        
        return bytes(compressed)

    def _hash_data(self, data: bytes, pos: int, length: int) -> int:
        """Simple hash for 3 bytes"""
        return (data[pos] << 16) | (data[pos+1] << 8) | data[pos+2]

    def _match_length(self, data: bytes, candidate: int, pos: int, max_pos: int) -> int:
        """Calculate match length"""
        length = 0
        max_len = min(self.lookahead_buffer, max_pos - pos)
        while length < max_len and data[candidate + length] == data[pos + length]:
            length += 1
        return length

    def _encode_token(self, offset: int, length: int) -> bytearray:
        """
        Encode LZ77 token into 2 bytes.
        Structure: 11 bits for offset, 4 bits for length.
        To distinguish from a literal (which starts with 0x80), the first
        byte of a token must not have its MSB set.
        
        Byte 1: [0][high 7 bits of offset]
        Byte 2: [low 4 bits of offset][4 bits of length]
        """
        # Ensure values are within the defined bit-range
        encoded_len = length - self.min_match_length
        
        # Byte 1: MSB is 0 (guaranteed by & 0x7F) + 7 bits of offset
        byte1 = (offset >> 4) & 0x7F
        # Byte 2: Lower 4 bits of offset shifted left, ORed with 4 bits of length
        byte2 = ((offset & 0x0F) << 4) | (encoded_len & 0x0F)
        
        return bytearray([byte1, byte2])


class LZ77Decompressor:
    def __init__(self):
        self.min_match_length = 3

    def decompress(self, data: bytes) -> bytes:
        """Decompress LZ77 compressed data"""
        decompressed = bytearray()
        pos = 0
        
        while pos < len(data):
            # Check for literal marker (MSB is 1)
            if data[pos] == 0x80:
                if pos + 1 >= len(data):
                    # Incomplete literal at end of stream
                    raise ValueError("Corrupted data: incomplete literal")
                decompressed.append(data[pos + 1])
                pos += 2
            else:  # Token (MSB is 0)
                if pos + 1 >= len(data):
                    # Incomplete token at end of stream
                    raise ValueError("Corrupted data: incomplete token")
                
                byte1 = data[pos]
                byte2 = data[pos + 1]
                
                # Reconstruct offset and length based on the defined structure
                # Offset: 7 bits from byte1, 4 bits from byte2
                offset = ((byte1 & 0x7F) << 4) | (byte2 >> 4)
                # Length: 4 bits from byte2
                length = (byte2 & 0x0F) + self.min_match_length
                
                if offset == 0:
                    raise ValueError("Invalid offset 0 in token")
                if offset > len(decompressed):
                    raise ValueError("Invalid offset in compressed data (points beyond decompressed buffer)")
                
                start = len(decompressed) - offset
                for _ in range(length):
                    decompressed.append(decompressed[start])
                    start += 1
                
                pos += 2
        
        return bytes(decompressed)