from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="deseq2-wrapper",
    version="0.1.1",
    author="Pai Li, Claude Opus 4",
    author_email="lipai@umd.edu",
    description="Python wrapper for DESeq2 RNA-seq differential expression analysis in Arabidopsis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/deseq2-wrapper",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pandas>=1.0.0",
        "numpy>=1.18.0",
        "rpy2>=3.0.0",
        "openpyxl>=3.0.0",  # For Excel file support
    ],
    package_data={
        "deseq2_wrapper": ["deseq2_functions.R"],
    },
    include_package_data=True,
    keywords="RNA-seq, differential expression, DESeq2, bioinformatics, transcriptomics",
)