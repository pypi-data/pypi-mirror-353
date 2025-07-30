#!/usr/bin/env python3
"""
VarAnnote - Comprehensive Variant Analysis & Annotation Suite
A powerful toolkit for genomic variant annotation and clinical interpretation
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="varannote",
    version="1.0.0",
    author="Ata Umut ÖZSOY",
    author_email="ataumut7@gmail.com",
    description="Comprehensive Variant Analysis & Annotation Suite",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/AtaUmutOZSOY/VarAnnote",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "varannote=varannote.cli:main",
            "variant-annotator=varannote.tools.annotator:main",
            "pathogenicity-predictor=varannote.tools.pathogenicity:main",
            "pharmacogenomics-analyzer=varannote.tools.pharmacogenomics:main",
            "population-freq-calculator=varannote.tools.population_freq:main",
            "compound-het-detector=varannote.tools.compound_het:main",
            "segregation-analyzer=varannote.tools.segregation:main",
        ],
    },
    keywords="bioinformatics genomics variant-annotation clinical-genomics",
    project_urls={
        "Bug Reports": "https://github.com/AtaUmutOZSOY/VarAnnote/issues",
        "Source": "https://github.com/AtaUmutOZSOY/VarAnnote",
        "Documentation": "https://varannote.readthedocs.io/",
    },
    include_package_data=True,
    zip_safe=False,
) 