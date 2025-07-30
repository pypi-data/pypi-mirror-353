# GAFOC/core/huffman.pyx

import heapq
from collections import Counter
import struct

# Using cdef for C-level speed in the node and class definitions
cdef class HuffmanNode:
    cdef public int symbol
    cdef public long freq
    cdef public object left, right

    def __cinit__(self, symbol=-1, freq=0, left=None, right=None):
        self.symbol = symbol
        self.freq = freq
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < (<HuffmanNode>other).freq

cdef class HuffmanEncoder:
    def encode(self, bytes data):
        cdef int data_len = len(data)
        if data_len == 0:
            return b''

        # 1. Build frequency table (Counter is fast as it's C-based)
        freq_table = Counter(data)

        # 2. Build Huffman Tree (using heapq is efficient)
        cdef list heap = [HuffmanNode(s, f) for s, f in freq_table.items()]
        heapq.heapify(heap)

        cdef HuffmanNode left, right, merged, root
        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            merged = HuffmanNode(freq=left.freq + right.freq, left=left, right=right)
            heapq.heappush(heap, merged)
        
        root = heap[0] if heap else None
        
        # 3. Generate codes from tree
        # The codes list will store bit-strings as bytes for efficiency
        cdef list codes = [b""] * 256
        self._generate_codes(root, b"", codes)

        # 4. Serialize frequency table into header
        cdef bytearray header = bytearray()
        cdef int num_entries = len(freq_table)
        header.extend(struct.pack('>I', num_entries))
        for symbol, frequency in freq_table.items():
            header.extend(struct.pack('>BQ', symbol, frequency))
        
        # 5. Encode data without creating a massive intermediate string
        cdef bytearray encoded_data = bytearray()
        cdef int bit_buffer = 0
        cdef int bit_count = 0

        # This loop is now extremely fast due to Cython's optimizations
        cdef int i, byte, bit
        cdef bytes code
        for i in range(data_len):
            byte = data[i]
            code = codes[byte]
            for bit_char in code:
                bit_buffer = (bit_buffer << 1) | (bit_char - 48) # '0' is 48
                bit_count += 1
                if bit_count == 8:
                    encoded_data.append(bit_buffer)
                    bit_buffer = 0
                    bit_count = 0
        
        # Handle remaining bits in the buffer (padding)
        cdef int padding_amount = 0
        if bit_count > 0:
            bit_buffer <<= (8 - bit_count)
            encoded_data.append(bit_buffer)
            padding_amount = 8 - bit_count

        return bytes(header) + padding_amount.to_bytes(1, 'big') + bytes(encoded_data)

    cdef void _generate_codes(self, HuffmanNode node, bytes current_code, list codes):
        if node is None:
            return
        if node.symbol != -1:
            codes[node.symbol] = current_code
            return
        self._generate_codes(node.left, current_code + b"0", codes)
        self._generate_codes(node.right, current_code + b"1", codes)


cdef class HuffmanDecoder:
    def decode(self, bytes data):
        cdef int data_len = len(data)
        if data_len == 0:
            return b''

        # 1. Deserialize header to rebuild frequency table
        if data_len < 4: raise ValueError("Corrupted data: Incomplete header.")
        cdef int num_entries = struct.unpack('>I', data[:4])[0]
        
        cdef dict freq_table = {}
        cdef int pos = 4
        cdef int entry_size = 9 # symbol (B) + frequency (Q)
        cdef int header_end = pos + (num_entries * entry_size)
        if data_len < header_end: raise ValueError("Corrupted data: Header size mismatch.")

        cdef int symbol
        cdef long frequency
        for _ in range(num_entries):
            symbol, frequency = struct.unpack('>BQ', data[pos : pos + entry_size])
            freq_table[symbol] = frequency
            pos += entry_size
            
        # 2. Rebuild the exact same Huffman tree
        cdef list heap = [HuffmanNode(s, f) for s, f in freq_table.items()]
        heapq.heapify(heap)
        
        cdef HuffmanNode left, right, merged, root
        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            merged = HuffmanNode(freq=left.freq + right.freq, left=left, right=right)
            heapq.heappush(heap, merged)
        
        root = heap[0] if heap else None
        
        if root is None: return b''
        if root.left is None and root.right is None: # Single symbol case
            return bytes([root.symbol] * root.freq)

        # 3. Decode the data stream
        cdef int padding_amount = data[pos]
        cdef int data_body_pos = pos + 1
        cdef int data_body_len = data_len - data_body_pos

        cdef bytearray decoded_output = bytearray()
        cdef HuffmanNode current_node = root
        cdef int i, j, byte, bit
        
        for i in range(data_body_len):
            byte = data[data_body_pos + i]
            # If it's the last byte, don't read the padding bits
            bits_to_read = 8 if (i < data_body_len - 1) else (8 - padding_amount)

            for j in range(bits_to_read):
                bit = (byte >> (7 - j)) & 1
                if bit == 0:
                    current_node = current_node.left
                else:
                    current_node = current_node.right
                
                if current_node.left is None and current_node.right is None:
                    decoded_output.append(current_node.symbol)
                    current_node = root
        
        return bytes(decoded_output)