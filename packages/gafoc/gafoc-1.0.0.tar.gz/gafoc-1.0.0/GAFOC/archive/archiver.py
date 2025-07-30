# في ملف archiver.py

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
        data_chunks = []

        # 1. ضغط الملفات وتجهيز البيانات والإدخالات الأولية (بدون offset)
        for file_path in files:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            with open(file_path, 'rb') as f:
                data = f.read()

            compressed = self.compressor.compress_data(data)
            data_chunks.append(compressed)
            
            # offset سيتم حسابه لاحقاً
            entries.append(ArchiveEntry(
                filename=os.path.basename(file_path),
                offset=0, 
                size=len(data),
                compressed_size=len(compressed),
                is_compressed=True
            ))

        # 2. حساب حجم الهيدر + جدول الملفات (Metadata) لتحديد نقطة بداية البيانات
        # b'GAFOARCH' (8) + compression_level (1) + num_files (2)
        header_size = 11
        
        # حجم جدول الإدخالات
        entries_metadata_size = 0
        for entry in entries:
            # len(filename) (2) + filename + offset (8) + size (8) + compressed_size (8) + is_compressed (1)
            entries_metadata_size += 2 + len(entry.filename.encode('utf-8')) + 8 + 8 + 8 + 1
        
        total_metadata_size = header_size + entries_metadata_size

        # 3. تحديث الإزاحات (Offsets) المطلقة الصحيحة لكل ملف
        current_offset = total_metadata_size
        for i, entry in enumerate(entries):
            # تعيين الإزاحة المطلقة من بداية ملف الأرشيف
            entries[i].offset = current_offset
            # تحديث الإزاحة للملف التالي
            current_offset += entry.compressed_size

        # 4. كتابة ملف الأرشيف بالكامل
        try:
            with open(archive_path, 'wb') as f:
                # كتابة الهيدر الأساسي
                f.write(b'GAFOARCH')
                f.write(struct.pack('>B', self.compression_level))
                f.write(struct.pack('>H', len(files)))

                # كتابة جدول الإدخالات مع الإزاحات الصحيحة
                for entry in entries:
                    filename_bytes = entry.filename.encode('utf-8')
                    f.write(struct.pack('>H', len(filename_bytes)))
                    f.write(filename_bytes)
                    f.write(struct.pack('>Q', entry.offset))
                    f.write(struct.pack('>Q', entry.size))
                    f.write(struct.pack('>Q', entry.compressed_size))
                    f.write(struct.pack('>B', int(entry.is_compressed)))
                
                # كتابة بيانات الملفات المضغوطة واحداً تلو الآخر
                for chunk in data_chunks:
                    f.write(chunk)
        except IOError as e:
            raise ArchiveError(f"Archive creation failed: {str(e)}") from e