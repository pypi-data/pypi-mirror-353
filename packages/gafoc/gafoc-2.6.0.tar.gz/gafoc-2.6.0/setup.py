# setup.py
# This setup script REQUIRES a C compiler and Cython to be installed.
# It will fail if the Cython extensions cannot be built.

import os
from setuptools import setup, find_packages, Extension

try:
    from Cython.Build import cythonize
except ImportError:
    # This is a critical error. The user MUST have Cython.
    raise RuntimeError(
        "Cython is required to build this package. "
        "Please install it with 'pip install cython'"
    )

# --- Read README for long description on PyPI ---
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "A high-performance file compression and archiving library."


# --- Define the required C extension modules ---
# The installation will fail if these .pyx files are not found or cannot be compiled.
extensions = [
    Extension(
        "GAFOC.core.huffman", # The full import path for the compiled module
        [os.path.join("GAFOC", "core", "huffman.pyx")]
    ),
    # Add lz77 back here if you decide to use your own implementation again
    # Extension(
    #     "GAFOC.core.lz77",
    #     [os.path.join("GAFOC", "core", "lz77.pyx")]
    # ),
]

# --- Main setup() function ---
setup(
    # --- Project Metadata ---
    name="gafoc",
    version="2.6.0", # Version reflecting the new build philosophy
    author="Gafoo",
    author_email="gafarssprts@gmail.com",
    description="A high-performance file compression library (requires C compiler).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gafoo173/",

    # --- Package Configuration ---
    packages=find_packages(),
    
    # This is now a hard requirement. The setup will fail if cythonize fails.
    ext_modules=cythonize(
        extensions,
        compiler_directives={'language_level' : "3"},
        # You can enable this to get an HTML report on C-code generation
        # annotate=True 
    ),
    
    # Ensure .pyx files are included in the source distribution (sdist)
    # so that pip can find them when building from source.
    include_package_data=True,

    # --- Dependencies ---
    install_requires=[
        'lz4',
        'zstandard',
        'brotli',
    ],
    
    # We can still give pip a hint that Cython is needed for setup,
    # though our check at the top is more explicit.
    setup_requires=['cython>=0.29'],
    
    # --- PyPI Classifiers ---
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        # NOTE: Be specific about OS if you only build wheels for specific ones
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Cython", # Added this classifier
        "Topic :: System :: Archiving :: Compression",
    ],
    
    python_requires=">=3.7",
    
    # C extensions are not zip-safe.
    zip_safe=False,
)