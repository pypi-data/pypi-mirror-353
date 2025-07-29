"""
DESeq2 Python Wrapper Package
Provides Python interface for RNA-seq differential expression analysis using DESeq2 and ClusterProfiler
"""

from .deseq2_wrapper import (
    check_r_libraries,
    load_r_functions,
    make_dds,
    compare_filter_annot,
    GO_from_DEGs,
    initialize
)

__version__ = "0.1.1"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Do not automatically initialize - let users call initialize() manually
# This prevents conflicts on Windows systems with Rtools