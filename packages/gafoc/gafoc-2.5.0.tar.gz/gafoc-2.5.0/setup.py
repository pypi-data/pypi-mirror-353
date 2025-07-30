# setup.py

from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
import os

# To find the GAFOC package correctly
# We are assuming setup.py is in the root directory, and GAFOC is a sub-directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GAFOC_DIR = os.path.join(BASE_DIR, "GAFOC")

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Define the C extension modules to be built by Cython
# This is the core of the change
extensions = [
    Extension(
        "GAFOC.core.huffman",
        [os.path.join(GAFOC_DIR, "core", "huffman.pyx")]
    ),
]

setup(
    name="gafoc",
    version="2.5.0", # Bump version for performance update
    author="Gafoo",
    author_email="gafarssprts@gmail.com",
    description="A high-performance file compression and archiving library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/gafoc", # Update this with your repo URL
    
    packages=find_packages(),
    
    ext_modules=cythonize(
        extensions,
        compiler_directives={'language_level' : "3"} # Use Python 3 semantics
    ),
    
    install_requires=[
        'lz4', # Still required by the high-level compressor
    ],

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: System :: Archiving :: Compression",
    ],
    python_requires=">=3.7",
    zip_safe=False,
)