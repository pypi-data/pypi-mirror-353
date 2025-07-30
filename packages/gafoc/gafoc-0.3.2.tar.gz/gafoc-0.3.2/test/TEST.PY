from gafoc.archive import GAFOArchiver, GAFOExtractor
import os

def check_files_exist(files):
    missing = [f for f in files if not os.path.exists(f)]
    if missing:
        raise FileNotFoundError(f"الملفات التالية غير موجودة: {missing}")

def compress_and_extract():
    try:
        files_to_compress = ["1.TXT", "2.TXT", "3.TXT"]
        archive_name = "archive.gafo"
        output_dir = "EXT"
        
        # التحقق من وجود الملفات
        check_files_exist(files_to_compress)
        
        # الضغط
        archiver = GAFOArchiver(compression_level=6)
        archiver.create_archive(files_to_compress, archive_name)
        print(f"تم ضغط {len(files_to_compress)} ملفات إلى {archive_name}")
        
        # فك الضغط
        if os.path.exists(output_dir):
            print(f"تحذير: المجلد {output_dir} موجود بالفعل، سيتم استبدال المحتويات")
            
        extractor = GAFOExtractor()
        extracted = extractor.extract_archive(archive_name, output_dir)
        print(f"تم استخراج {len(extracted)} ملفات إلى {output_dir}")
        
    except Exception as e:
        print(f"!خطأ: {e}")

if __name__ == "__main__":
    compress_and_extract()