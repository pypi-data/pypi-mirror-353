import os
import struct
from dataclasses import dataclass
from typing import List, Dict
from ..core.compression import GAFOCompressor
from ..exceptions import ArchiveError

@dataclass
class ArchiveEntry:
    filename: str
    offset: int
    size: int
    compressed_size: int
    is_compressed: bool

class GAFOArchiver:
    def __init__(self, compression_level: int = 6):
        self.compressor = GAFOCompressor(compression_level)
        self.compression_level = compression_level

    def create_archive(self, files: List[str], archive_path: str) -> None:
        """Create a GAFO archive containing multiple files"""
        if not files:
            raise ArchiveError("No files provided for archiving")
            
        entries = []
        compressed_data = bytearray()
        
        try:
            # Process each file
            for file_path in files:
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"File not found: {file_path}")
                    
                with open(file_path, 'rb') as f:
                    data = f.read()
                
                compressed = self.compressor.compress_data(data)
                
                entry = ArchiveEntry(
                    filename=os.path.basename(file_path),
                    offset=len(compressed_data),
                    size=len(data),
                    compressed_size=len(compressed),
                    is_compressed=True
                )
                
                entries.append(entry)
                compressed_data.extend(compressed)
            
            # Write archive file
            with open(archive_path, 'wb') as f:
                self._write_archive_header(f, len(files))
                self._write_file_entries(f, entries)
                f.write(compressed_data)
                
        except IOError as e:
            raise ArchiveError(f"Archive creation failed: {str(e)}") from e

    def _write_archive_header(self, file_obj, num_files: int) -> None:
        """Write archive header"""
        file_obj.write(b'GAFOARCH')
        file_obj.write(struct.pack('>B', self.compression_level))
        file_obj.write(struct.pack('>H', num_files))

    def _write_file_entries(self, file_obj, entries: List[ArchiveEntry]) -> None:
        """Write file entries table"""
        for entry in entries:
            filename_bytes = entry.filename.encode('utf-8')
            file_obj.write(struct.pack('>H', len(filename_bytes)))
            file_obj.write(filename_bytes)
            file_obj.write(struct.pack('>Q', entry.offset))
            file_obj.write(struct.pack('>Q', entry.size))
            file_obj.write(struct.pack('>Q', entry.compressed_size))
            file_obj.write(struct.pack('>B', int(entry.is_compressed)))