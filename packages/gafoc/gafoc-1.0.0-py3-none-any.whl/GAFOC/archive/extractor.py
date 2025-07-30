# extractor.py

import os
import struct
from typing import List
from dataclasses import dataclass
from ..core.decompression import GAFODecompressor
from ..exceptions import ArchiveError, ExtractionError

@dataclass
class ArchiveEntry:
    filename: str
    offset: int
    size: int
    compressed_size: int
    is_compressed: bool

class GAFOExtractor:
    def __init__(self):
        self.decompressor = GAFODecompressor()

    def extract_archive(self, archive_path: str, output_dir: str) -> List[str]:
        """Extract files from a GAFO archive"""
        if not os.path.exists(archive_path):
            raise FileNotFoundError(f"Archive not found: {archive_path}")
            
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        extracted_files = []
        try:
            with open(archive_path, 'rb') as f:
                entries = self._read_file_entries(f)
                
                for entry in entries:
                    f.seek(entry.offset)
                    compressed_data = f.read(entry.compressed_size)
                    
                    if len(compressed_data) != entry.compressed_size:
                        raise ExtractionError(f"Unexpected end of file while reading {entry.filename}")
                    
                    output_path = os.path.join(output_dir, entry.filename)
                    
                    if entry.is_compressed:
                        # *** الخطوة الحاسمة: استدعاء الدالة الصحيحة ***
                        file_data = self.decompressor.decompress_chunk(compressed_data)
                    else:
                        file_data = compressed_data
                    
                    with open(output_path, 'wb') as f_out:
                        f_out.write(file_data)
                    
                    extracted_files.append(output_path)
            
            return extracted_files
            
        except (IOError, ArchiveError, ExtractionError) as e:
            raise ExtractionError(f"Archive extraction failed: {str(e)}") from e
        except Exception as e:
            raise ExtractionError(f"An unexpected error occurred during extraction: {str(e)}") from e

    def _read_file_entries(self, file_obj) -> List[ArchiveEntry]:
        """Read archive header and the file entries table."""
        header = file_obj.read(8)
        if header != b'GAFOARCH':
            raise ArchiveError("Invalid GAFO archive format: Magic number mismatch")
            
        _ = struct.unpack('>B', file_obj.read(1))[0]
        num_files = struct.unpack('>H', file_obj.read(2))[0]
        
        if num_files == 0:
            return []

        entries = []
        for _ in range(num_files):
            try:
                filename_len_bytes = file_obj.read(2)
                if not filename_len_bytes: raise EOFError
                filename_len = struct.unpack('>H', filename_len_bytes)[0]
                filename = file_obj.read(filename_len).decode('utf-8')
                offset = struct.unpack('>Q', file_obj.read(8))[0]
                size = struct.unpack('>Q', file_obj.read(8))[0]
                compressed_size = struct.unpack('>Q', file_obj.read(8))[0]
                is_compressed = bool(struct.unpack('>B', file_obj.read(1))[0])
                entries.append(ArchiveEntry(filename, offset, size, compressed_size, is_compressed))
            except (struct.error, EOFError):
                raise ArchiveError("Archive is corrupted or has an incomplete entry table.")
        
        return entries