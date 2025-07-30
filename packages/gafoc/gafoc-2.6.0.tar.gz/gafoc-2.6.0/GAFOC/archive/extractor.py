# GAFOC/archive/extractor.py

import os
import struct
from typing import List
from dataclasses import dataclass
import traceback  # <-- 1. إضافة الاستيراد

# تأكد من أن هذه الاستيرادات صحيحة بالنسبة لهيكل مشروعك
from ..core.decompression import GAFODecompressor 
from ..exceptions import ArchiveError, ExtractionError

# تعريف dataclass إذا لم يكن موجودًا بالفعل
@dataclass
class ArchiveEntry:
    filename: str
    offset: int
    size: int
    compressed_size: int

class GAFOExtractor:
    def __init__(self):
        # الآن Extractor يعتمد على Decompressor
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
                entries, header_info = self._read_file_entries(f)
                
                for entry in entries:
                    f.seek(entry.offset)
                    compressed_data = f.read(entry.compressed_size)
                    
                    if len(compressed_data) != entry.compressed_size:
                        raise ExtractionError(f"Unexpected end of file while reading {entry.filename}")
                    
                    output_path = os.path.join(output_dir, entry.filename)
                    
                    # استخدم Decompressor لفك ضغط كل جزء
                    # نفترض أن GAFODecompressor لديه دالة decompress_chunk
                    file_data = self.decompressor.decompress_chunk(compressed_data)
                    
                    # التحقق من الحجم بعد فك الضغط (اختياري ولكن مهم)
                    if len(file_data) != entry.size:
                         print(f"Warning: Decompressed size mismatch for {entry.filename}. Expected {entry.size}, got {len(file_data)}.")


                    with open(output_path, 'wb') as f_out:
                        f_out.write(file_data)
                    
                    extracted_files.append(output_path)
            
            return extracted_files
            
        except (IOError, ArchiveError, ExtractionError) as e:
            # الأخطاء المتوقعة من المكتبة
            raise ExtractionError(f"Archive extraction failed: {str(e)}") from e
        except Exception as e:
            # 2. إضافة آلية كشف الأخطاء هنا
            print("\n>>> DEBUG: Original error in GAFOExtractor <<<")
            traceback.print_exc()
            print(">>> END DEBUG <<<\n")
            raise ExtractionError(f"An unexpected error occurred during extraction: {str(e)}") from e

    def _read_file_entries(self, file_obj) -> (List[ArchiveEntry], dict):
        """Read archive header and the file entries table."""
        header = file_obj.read(8)
        if header != b'GAFOARCH':
            raise ArchiveError("Invalid GAFO archive format: Magic number mismatch")
            
        compression_level = struct.unpack('>B', file_obj.read(1))[0]
        num_files = struct.unpack('>H', file_obj.read(2))[0]
        
        header_info = {'level': compression_level, 'num_files': num_files}

        if num_files == 0:
            return [], header_info

        entries = []
        for _ in range(num_files):
            try:
                # هذا الهيكل يجب أن يطابق تمامًا ما يكتبه Archiver
                filename_len_bytes = file_obj.read(2)
                if not filename_len_bytes: raise EOFError("Incomplete entry header.")
                filename_len = struct.unpack('>H', filename_len_bytes)[0]
                
                filename = file_obj.read(filename_len).decode('utf-8')
                
                offset = struct.unpack('>Q', file_obj.read(8))[0]
                size = struct.unpack('>Q', file_obj.read(8))[0]
                compressed_size = struct.unpack('>Q', file_obj.read(8))[0]
                
                entries.append(ArchiveEntry(
                    filename=filename,
                    offset=offset,
                    size=size,
                    compressed_size=compressed_size
                ))
            except (struct.error, EOFError, IndexError) as e:
                raise ArchiveError(f"Archive is corrupted or has an incomplete entry table: {e}")
        
        return entries, header_info