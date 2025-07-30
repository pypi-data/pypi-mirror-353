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
        
        try:
            with open(archive_path, 'rb') as f:
                entries = self._read_archive_header(f)
                archive_data = f.read()
            
            extracted_files = []
            
            for entry in entries:
                file_data = archive_data[entry.offset:entry.offset + entry.compressed_size]
                output_path = os.path.join(output_dir, entry.filename)
                
                if entry.is_compressed:
                    file_data = self.decompressor.decompress_data(file_data)[0]
                
                with open(output_path, 'wb') as f_out:
                    f_out.write(file_data)
                
                extracted_files.append(output_path)
            
            return extracted_files
            
        except Exception as e:
            raise ExtractionError(f"Archive extraction failed: {str(e)}") from e

    def _read_archive_header(self, file_obj) -> List[ArchiveEntry]:
        """Read archive header and file entries"""
        header = file_obj.read(8)
        if header != b'GAFOARCH':
            raise ArchiveError("Invalid GAFO archive format")
            
        compression_level = struct.unpack('>B', file_obj.read(1))[0]
        num_files = struct.unpack('>H', file_obj.read(2))[0]
        
        entries = []
        
        for _ in range(num_files):
            filename_len = struct.unpack('>H', file_obj.read(2))[0]
            filename = file_obj.read(filename_len).decode('utf-8')
            offset = struct.unpack('>Q', file_obj.read(8))[0]
            size = struct.unpack('>Q', file_obj.read(8))[0]
            compressed_size = struct.unpack('>Q', file_obj.read(8))[0]
            is_compressed = bool(struct.unpack('>B', file_obj.read(1))[0])
            
            entries.append(ArchiveEntry(
                filename=filename,
                offset=offset,
                size=size,
                compressed_size=compressed_size,
                is_compressed=is_compressed
            ))
        
        return entries