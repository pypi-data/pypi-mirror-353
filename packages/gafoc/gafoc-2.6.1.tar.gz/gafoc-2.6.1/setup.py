# setup.py - Final, Robust, and Portable

from setuptools import setup, find_packages, Extension

try:
    from Cython.Build import cythonize
except ImportError:
    raise RuntimeError("Cython is required to build this package. Please run 'pip install cython'")

# --- Read README for long description on PyPI ---
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "A high-performance file compression and archiving library."

# ==========================================================
#                  THE CRITICAL FIX
# Use simple, relative, slash-separated paths for extensions.
# Do NOT use os.path.join here.
# ==========================================================
extensions = [
    Extension(
        "GAFOC.core.huffman",
        ["GAFOC/core/huffman.pyx"] # <--- المسار النسبي الصحيح
    ),
    # Add other extensions here in the same way if needed in the future
    # Extension(
    #     "GAFOC.core.lz77",
    #     ["GAFOC/core/lz77.pyx"]
    # ),
]

# --- Main setup() function ---
setup(
    name="gafoc",
    version="2.6.1",  # <-- IMPORTANT: Increment the version!
    author="Gafoo",
    author_email="gafarssprts@gmail.com",
    description="A high-performance file compression library (requires C compiler).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gafoo173/GAFOC",

    packages=find_packages(),
    
    ext_modules=cythonize(
        extensions,
        compiler_directives={'language_level' : "3"},
    ),
    
    include_package_data=True,

    install_requires=[
        'lz4',
        'zstandard',
        'brotli',
    ],
    
    setup_requires=['cython>=0.29'],
    
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Cython",
        "Topic :: System :: Archiving :: Compression",
    ],
    
    python_requires=">=3.7",
    zip_safe=False,
)