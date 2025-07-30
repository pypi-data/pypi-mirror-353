# GAFOC - High-Performance File Archiver

**GAFOC is a modern, high-performance Python library for file compression and archiving, built for speed and reliability.**

It leverages the lightning-fast **LZ4** compression algorithm for its core operations, providing an excellent balance between incredible speed and solid compression ratios. This makes it ideal for applications requiring rapid archiving and extraction, such as data logging, network transfers, and application resource management.

---

## Core Features

*   🚀 **Blazing Fast Performance:** Powered by the C-based LZ4 engine, GAFOC achieves extremely high compression and decompression speeds, easily handling large files and high-throughput scenarios.
*   🗄️ **Multi-File Archiving:** Seamlessly create `.gafo` archives containing multiple files and folders, and extract them with ease.
*   🧬 **Hybrid Compression (Optional):** Applies an optional Huffman coding layer on top of LZ4 output, which can further improve compression ratios for certain types of data.
*   🔧 **Adjustable Compression Levels:** Fine-tune the trade-off between speed and compression ratio using LZ4's versatile compression levels (0-16).
*   🔒 **Robust & Reliable:** Built on a proven, industry-standard compression library, ensuring data integrity and preventing corruption.
*   💻 **Developer-Friendly API:** A simple and intuitive API for both archiving and extraction, making it easy to integrate into your Python projects.
*   ✨ **Bonus: GUI Application:** Comes with a professional, modern graphical user interface (`GAFOC Pro`) for easy, everyday use, featuring a unique compression comparison tool.


```markdown
**A Note on a Legacy Engine:** Versions of GAFOC prior to `2.0.1` featured a custom, pure-Python implementation of LZ77. While a great learning experience, it was removed in favor of the LZ4 engine to resolve performance and data corruption issues with large binary files. The legacy implementation can be found in the project's history for educational purposes.
## Installation

The library is available on PyPI:

```bash
pip install gafoc
pip install customtkinter CTkMessagebox # For the GUI application