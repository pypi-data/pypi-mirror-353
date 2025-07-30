from typing import Dict, List, Tuple
from collections import defaultdict
import heapq

class LZ77Compressor:
    def __init__(self, compression_level: int):
        self.window_size = 2 ** (12 + compression_level // 3)
        self.lookahead_buffer = 2 ** (4 + compression_level // 3)
        self.min_match_length = 3

    def compress(self, data: bytes) -> bytes:
        """LZ77 compression with improved search using hash table"""
        compressed = bytearray()
        pos = 0
        len_data = len(data)
        hash_table = defaultdict(list)
        
        while pos < len_data:
            best_offset, best_length = 0, 0
            
            # Only search if we have enough data for a match
            if pos >= self.min_match_length and pos + self.min_match_length <= len_data:
                current_hash = self._hash_data(data, pos, self.min_match_length)
                
                # Check all positions with the same hash
                for candidate in hash_table.get(current_hash, []):
                    if pos - candidate > self.window_size:
                        continue
                        
                    length = self._match_length(data, candidate, pos, len_data)
                    
                    if length > best_length:
                        best_length = length
                        best_offset = pos - candidate
                        if best_length == self.lookahead_buffer:
                            break
                
                # Update hash table
                if pos + self.min_match_length <= len_data:
                    hash_table[current_hash].append(pos)
            
            if best_length >= self.min_match_length:
                compressed.extend(self._encode_token(best_offset, best_length))
                pos += best_length
            else:
                compressed.append(0x80)  # Literal marker
                compressed.append(data[pos])
                pos += 1
        
        return bytes(compressed)

    def _hash_data(self, data: bytes, pos: int, length: int) -> int:
        """Simple rolling hash for quick matching"""
        return (data[pos] << 16) | (data[pos+1] << 8) | data[pos+2]

    def _match_length(self, data: bytes, candidate: int, pos: int, max_pos: int) -> int:
        """Calculate match length between candidate and current position"""
        length = 0
        max_length = min(self.lookahead_buffer, max_pos - pos)
        
        while length < max_length and data[candidate + length] == data[pos + length]:
            length += 1
            
        return length

    def _encode_token(self, offset: int, length: int) -> bytearray:
        """Encode LZ77 token (12-bit offset, 6-bit length)"""
        token = bytearray()
        token.append((offset >> 4) & 0xFF)
        token.append(((offset & 0x0F) << 4) | ((length - self.min_match_length) & 0x3F))
        return token


class LZ77Decompressor:
    def __init__(self):
        self.min_match_length = 3

    def decompress(self, data: bytes) -> bytes:
        """Decompress LZ77 compressed data"""
        decompressed = bytearray()
        pos = 0
        
        while pos < len(data):
            if data[pos] & 0x80:  # Literal
                if pos + 1 >= len(data):
                    break
                decompressed.append(data[pos + 1])
                pos += 2
            else:  # Token
                if pos + 1 >= len(data):
                    break
                
                offset = ((data[pos] & 0x7F) << 4) | ((data[pos + 1] >> 4) & 0x0F)
                length = (data[pos + 1] & 0x3F) + self.min_match_length
                
                # Validate offset
                if offset > len(decompressed):
                    raise ValueError("Invalid offset in compressed data")
                
                # Copy from sliding window
                start = len(decompressed) - offset
                for i in range(length):
                    decompressed.append(decompressed[start + i])
                
                pos += 2
        
        return bytes(decompressed)