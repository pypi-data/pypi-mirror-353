# GAFOC - The Smart Compression Toolkit

**GAFOC is a modern, high-performance Python library and desktop application designed to achieve optimal file compression by intelligently selecting the best compression strategy for your data.**

Instead of relying on a single algorithm, GAFOC's **Smart Compression** engine benchmarks multiple state-of-the-art hybrid pipelines (like `LZ4+Huffman`, `Zstd+Huffman`, etc.) for each file and automatically chooses the one that yields the smallest size. This makes it the perfect tool for archiving, storage optimization, and data transfer where final size is critical.

---

## Key Features

*   🧠 **Smart Compression Engine:** Automatically tests multiple advanced compression pipelines and selects the most effective one for each file, guaranteeing the best possible compression ratio from its available methods.
*   🚀 **High-Performance Backends:** Leverages industry-standard, C-based libraries like **LZ4**, **Zstandard**, **Brotli**, and **Zlib** for its core operations, ensuring both speed and reliability.
*   🧬 **Signature Hybrid Compression:** Each pipeline is enhanced with GAFOC's custom, high-speed Huffman coding layer (Cython-optimized) to squeeze out extra bytes, often outperforming the raw base algorithms.
*   🎛️ **Full User Control:** Don't want to use Smart mode? The tool provides full control to manually select a base algorithm (like Brotli or LZ4) and choose whether to apply the Huffman layer, giving you power over the speed-vs-ratio trade-off.
*   ✨ **Professional GUI Application:** Includes a sleek, modern, and responsive desktop application (`GAFOC Ultimate`) built with CustomTkinter. No more command-line struggles.
*   📊 **Built-in Benchmark Tool:** A dedicated tool to visually compare the performance (size, ratio, and time) of all available compression methods on your specific files, helping you understand your data better.

## What is Smart Compression?

When you choose "GAFOC Smart", the engine performs the following steps in the background:

1.  It takes your input file.
2.  It runs it through several powerful compression pipelines:
    *   LZ4 + GAFOC Huffman
    *   Zstandard + GAFOC Huffman
    *   Brotli + GAFOC Huffman
    *   Zlib + GAFOC Huffman
3.  It compares the size of all the results.
4.  It automatically saves your file using **only the pipeline that produced the smallest output.**

This process may take a few extra seconds, but it ensures you're not leaving any potential savings on the table.

## Installation

The library and its dependencies are available on PyPI:

```bash
# For the core library
pip install gafoc

# For the GUI application and all features
pip install customtkinter CTkMessagebox lz4 zstandard brotli
Use code with caution.
Markdown
GAFOC Ultimate - The Desktop App
The included GUI provides an intuitive interface for all features:
Smart Compress: Select a file, and let GAFOC figure out the rest.
Custom Compress: Choose your own base algorithm and toggle the Huffman layer.
Decompress: Easily decompress any .gafoc file.
Benchmark Tool: See for yourself how each algorithm performs on your data.