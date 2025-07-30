# GAFOC/core/huffman.py

import heapq
from collections import Counter
import struct

class HuffmanNode:
    """A node for the Huffman tree."""
    def __init__(self, symbol=None, freq=0, left=None, right=None):
        self.symbol = symbol  # The byte value (0-255)
        self.freq = freq      # The frequency of the symbol
        self.left = left      # Left child node
        self.right = right    # Right child node

    # This allows nodes to be compared in the min-heap
    def __lt__(self, other):
        return self.freq < other.freq

class HuffmanEncoder:
    def __init__(self):
        self.codes = {}
        self.root = None

    def _build_frequency_table(self, data: bytes):
        """Calculates the frequency of each byte in the data."""
        return Counter(data)

    def _build_heap(self, freq_table):
        """Creates a min-heap of Huffman nodes from the frequency table."""
        heap = [HuffmanNode(symbol=s, freq=f) for s, f in freq_table.items()]
        heapq.heapify(heap)
        return heap

    def _build_tree(self, heap):
        """Builds the Huffman tree from the min-heap."""
        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            merged = HuffmanNode(freq=left.freq + right.freq, left=left, right=right)
            heapq.heappush(heap, merged)
        self.root = heap[0] if heap else None

    def _generate_codes(self, node, current_code):
        """Recursively generates codes for each symbol from the Huffman tree."""
        if node is None:
            return
        if node.symbol is not None:
            self.codes[node.symbol] = current_code
            return
        self._generate_codes(node.left, current_code + "0")
        self._generate_codes(node.right, current_code + "1")

    def _get_encoded_text(self, data: bytes) -> str:
        """Converts the input data into a single string of bits."""
        return "".join([self.codes[byte] for byte in data])
        
    def _pad_encoded_text(self, encoded_text: str):
        """Pads the bit string to make its length a multiple of 8."""
        extra_padding = 8 - (len(encoded_text) % 8)
        if extra_padding == 8:
            extra_padding = 0
            
        padded_text = encoded_text + ('0' * extra_padding)
        return padded_text, extra_padding

    def _get_byte_array(self, padded_text: str) -> bytes:
        """Converts the padded bit string into a byte array."""
        byte_array = bytearray()
        for i in range(0, len(padded_text), 8):
            byte = padded_text[i:i+8]
            byte_array.append(int(byte, 2))
        return bytes(byte_array)

    def _serialize_header(self, freq_table) -> bytes:
        """Serializes the frequency table into a byte header."""
        # Header Format: Number of unique symbols (4 bytes, unsigned int)
        # Followed by [Symbol (1 byte), Frequency (8 bytes, unsigned long long)] for each symbol.
        num_entries = len(freq_table)
        header = struct.pack('>I', num_entries)
        for symbol, frequency in freq_table.items():
            header += struct.pack('>BQ', symbol, frequency)
        return header

    def encode(self, data: bytes) -> bytes:
        """The main encoding function."""
        if not data:
            return b''

        # 1. Build frequency table and Huffman tree
        freq_table = self._build_frequency_table(data)
        heap = self._build_heap(freq_table)
        self._build_tree(heap)
        
        # 2. Generate codes from the tree
        self._generate_codes(self.root, "")
        
        # 3. Convert data to bit string
        encoded_text = self._get_encoded_text(data)
        
        # 4. Pad the bit string and convert to bytes
        padded_text, padding_amount = self._pad_encoded_text(encoded_text)
        byte_array = self._get_byte_array(padded_text)
        
        # 5. Create the final output
        header = self._serialize_header(freq_table)
        padding_byte = padding_amount.to_bytes(1, 'big')
        
        return header + padding_byte + byte_array


class HuffmanDecoder:
    def _deserialize_header(self, data: bytes):
        """Deserializes the header to rebuild the frequency table."""
        if len(data) < 4:
            raise ValueError("Corrupted Huffman data: Incomplete header.")
        
        num_entries = struct.unpack('>I', data[:4])[0]
        freq_table = {}
        pos = 4
        entry_size = 9  # 1 byte for symbol, 8 bytes for frequency (Q)
        
        header_end = pos + (num_entries * entry_size)
        if len(data) < header_end:
            raise ValueError("Corrupted Huffman data: Header size mismatch.")

        for _ in range(num_entries):
            symbol, frequency = struct.unpack('>BQ', data[pos : pos + entry_size])
            freq_table[symbol] = frequency
            pos += entry_size
        
        # The data starts after the frequency table
        return freq_table, pos

    def decode(self, data: bytes) -> bytes:
        """The main decoding function."""
        if not data:
            return b''

        # 1. Rebuild the frequency table and Huffman tree
        freq_table, data_start_pos = self._deserialize_header(data)
        encoder_for_tree = HuffmanEncoder() # Use encoder's logic to build the tree
        heap = encoder_for_tree._build_heap(freq_table)
        encoder_for_tree._build_tree(heap)
        root = encoder_for_tree.root
        
        if root is None: # Handle case of empty or single-symbol data
            if freq_table:
                symbol = list(freq_table.keys())[0]
                count = freq_table[symbol]
                return bytes([symbol] * count)
            return b''

        # 2. Get padding info and the actual compressed data
        padding_amount = data[data_start_pos]
        encoded_data = data[data_start_pos + 1:]

        # 3. Convert data bytes back to a bit string
        bit_string = "".join([bin(byte)[2:].rjust(8, '0') for byte in encoded_data])
        
        # 4. Remove padding
        if padding_amount > 0:
            bit_string = bit_string[:-padding_amount]
        
        # 5. Traverse the tree to decode the bit string
        decoded_output = bytearray()
        current_node = root
        for bit in bit_string:
            if bit == '0':
                current_node = current_node.left
            else:
                current_node = current_node.right
            
            if current_node.symbol is not None:
                decoded_output.append(current_node.symbol)
                current_node = root
                
        return bytes(decoded_output)