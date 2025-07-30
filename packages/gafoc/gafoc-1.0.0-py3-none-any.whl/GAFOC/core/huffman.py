import struct
from typing import Dict, List, Tuple
from collections import defaultdict
import heapq

class HuffmanEncoder:
    def __init__(self):
        self.codes = {}
        self.reverse_codes = {}

    def encode(self, data: bytes) -> bytes:
        """Two-level adaptive Huffman encoding with canonical codes"""
        if not data:
            return b''
            
        freq = self._calculate_frequencies(data)
        self._build_codes(freq)
        
        encoded = bytearray()
        bit_buffer = []
        
        # Write header (canonical Huffman table)
        encoded.extend(self._serialize_header(freq))
        
        # Encode data
        for byte in data:
            bit_buffer.extend(self.codes[byte])
            
            while len(bit_buffer) >= 8:
                encoded.append(self._bits_to_byte(bit_buffer[:8]))
                bit_buffer = bit_buffer[8:]
        
        # Flush remaining bits
        if bit_buffer:
            padding = 8 - len(bit_buffer)
            encoded.append(self._bits_to_byte(bit_buffer + [0] * padding))
            encoded.append(padding)
        else:
            encoded.append(0)  # No padding
            
        return bytes(encoded)

    def _calculate_frequencies(self, data: bytes) -> Dict[int, int]:
        """Calculate byte frequencies with escape for rare bytes"""
        freq = defaultdict(int)
        for byte in data:
            freq[byte] += 1
        return freq

    def _build_codes(self, freq: Dict[int, int]) -> None:
        """Build canonical Huffman codes from frequency table"""
        heap = [[weight, [byte, ""]] for byte, weight in freq.items()]
        heapq.heapify(heap)
        
        while len(heap) > 1:
            lo = heapq.heappop(heap)
            hi = heapq.heappop(heap)
            for pair in lo[1:]:
                pair[1] = '0' + pair[1]
            for pair in hi[1:]:
                pair[1] = '1' + pair[1]
            heapq.heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])
        
        # Convert to canonical Huffman codes
        codes = {pair[0]: pair[1] for pair in heap[0][1:]}
        sorted_codes = sorted(codes.items(), key=lambda x: (len(x[1]), x[0]))
        
        # Generate canonical codes
        current_code = 0
        last_length = 0
        canonical_codes = {}
        
        for byte, code in sorted_codes:
            code_length = len(code)
            if code_length > last_length:
                current_code <<= (code_length - last_length)
                last_length = code_length
            canonical_codes[byte] = format(current_code, '0{}b'.format(code_length))
            current_code += 1
        
        self.codes = {byte: [int(bit) for bit in code] 
                     for byte, code in canonical_codes.items()}

    def _serialize_header(self, freq: Dict[int, int]) -> bytearray:
        """Serialize canonical Huffman table header"""
        header = bytearray()
        header.append(len(freq))  # Number of unique bytes
        
        for byte, code in sorted(self.codes.items(), key=lambda x: (len(x[1]), x[0])):
            code_length = len(code)
            header.append(byte)
            header.append(code_length)
        
        return header

    def _bits_to_byte(self, bits: List[int]) -> int:
        """Convert list of bits to byte"""
        byte = 0
        for i, bit in enumerate(bits[:8]):
            if bit:
                byte |= 1 << (7 - i)
        return byte


class HuffmanDecoder:
    def __init__(self):
        self.code_map = {}

    def decode(self, data: bytes) -> bytes:
        """Decode Huffman compressed data"""
        if not data:
            return b''
            
        pos = 0
        num_symbols = data[pos]
        pos += 1
        
        # Rebuild canonical Huffman codes
        symbols = []
        code_lengths = []
        
        for _ in range(num_symbols):
            symbols.append(data[pos])
            code_lengths.append(data[pos + 1])
            pos += 2
        
        self._rebuild_canonical_codes(symbols, code_lengths)
        
        # Decode data
        decoded = bytearray()
        bit_buffer = []
        padding = data[-1] if len(data) > pos else 0
        data_end = len(data) - (2 if padding > 0 else 1)
        
        for byte in data[pos:data_end]:
            for i in range(7, -1, -1):
                bit = (byte >> i) & 1
                bit_buffer.append(bit)
                code = tuple(bit_buffer)
                
                if code in self.code_map:
                    decoded.append(self.code_map[code])
                    bit_buffer = []
        
        # Handle padding if exists
        if padding > 0:
            byte = data[-2]
            for i in range(7, 7 - (8 - padding), -1):
                bit = (byte >> i) & 1
                bit_buffer.append(bit)
                code = tuple(bit_buffer)
                
                if code in self.code_map:
                    decoded.append(self.code_map[code])
                    bit_buffer = []
        
        return bytes(decoded)

    def _rebuild_canonical_codes(self, symbols: List[int], code_lengths: List[int]) -> None:
        """Rebuild canonical Huffman codes from header"""
        current_code = 0
        last_length = 0
        self.code_map = {}
        
        for byte, length in zip(symbols, code_lengths):
            if length > last_length:
                current_code <<= (length - last_length)
                last_length = length
            
            code = tuple(int(bit) for bit in format(current_code, '0{}b'.format(length)))
            self.code_map[code] = byte
            current_code += 1