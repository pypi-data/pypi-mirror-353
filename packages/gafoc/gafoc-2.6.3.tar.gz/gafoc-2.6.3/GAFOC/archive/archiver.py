# GAFOC/archive/archiver.py
import os
import struct
from dataclasses import dataclass
from typing import List
from ..core.compression import GAFOCompressor
from ..exceptions import ArchiveError

@dataclass
class ArchiveEntry:
    filename: str
    offset: int
    size: int
    compressed_size: int

class GAFOArchiver:
    def __init__(self, compression_level: int = 6):
        self.compressor = GAFOCompressor(compression_level)
        self.compression_level = compression_level

    def create_archive(self, files: List[str], archive_path: str) -> None:
        if not files:
            raise ArchiveError("No files provided for archiving")

        entries = []
        data_chunks = []

        for file_path in files:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            # ===============================================
            #  التصحيح الحاسم: استخدام 'rb' لقراءة أي نوع من الملفات
            # ===============================================
            with open(file_path, 'rb') as f:
                data = f.read()

            compressed = self.compressor.compress_data(data)
            data_chunks.append(compressed)
            
            entries.append(ArchiveEntry(
                filename=os.path.basename(file_path),
                offset=0, # سيتم تحديثه لاحقًا
                size=len(data),
                compressed_size=len(compressed)
            ))
        
        # حساب حجم الهيدر + جدول الملفات لتحديد نقطة بداية البيانات
        header_size = 8 + 1 + 2  # b'GAFOARCH' + level + num_files
        entries_metadata_size = 0
        for entry in entries:
            # Filename_len(2) + filename + offset(8) + size(8) + compressed_size(8)
            entries_metadata_size += 2 + len(entry.filename.encode('utf-8')) + 8 + 8 + 8
        
        total_metadata_size = header_size + entries_metadata_size

        # تحديث الإزاحات (Offsets) المطلقة الصحيحة
        current_offset = total_metadata_size
        for i, entry in enumerate(entries):
            entries[i].offset = current_offset
            current_offset += entry.compressed_size

        try:
            # ===============================================
            #  التأكيد: استخدام 'wb' لكتابة الملف كثنائي
            # ===============================================
            with open(archive_path, 'wb') as f:
                f.write(b'GAFOARCH')
                f.write(struct.pack('>B', self.compression_level))
                f.write(struct.pack('>H', len(files)))

                for entry in entries:
                    filename_bytes = entry.filename.encode('utf-8')
                    f.write(struct.pack('>H', len(filename_bytes)))
                    f.write(filename_bytes)
                    f.write(struct.pack('>Q', entry.offset))
                    f.write(struct.pack('>Q', entry.size))
                    f.write(struct.pack('>Q', entry.compressed_size))
                
                for chunk in data_chunks:
                    f.write(chunk)
        except IOError as e:
            raise ArchiveError(f"Archive creation failed: {str(e)}") from e