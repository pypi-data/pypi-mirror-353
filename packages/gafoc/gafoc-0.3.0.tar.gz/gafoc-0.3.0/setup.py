from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gafoc",
    version="0.3.0",
    author="Gafoo",
    author_email="gafarssprts@gmail.com",
    description="Advanced file compression library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gafoo173/Calculators",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        'console_scripts': [
            'gafoc = gafoc.cli:main',
        ],
    },
)