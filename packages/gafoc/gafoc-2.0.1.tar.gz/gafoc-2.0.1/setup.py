# setup.py

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gafoc",
    version="2.0.1", # New major version for the new engine
    author="Gafoo",
    author_email="gafarssprts@gmail.com",
    description="An efficient and fast file compression and archiving library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gafoo173/", # Suggesting a new repo for the project
    
    packages=find_packages(),
    
    # Add lz4 as a required dependency
    install_requires=[
        'lz4',
    ],

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: System :: Archiving :: Compression",
    ],
    python_requires=">=3.7",
)