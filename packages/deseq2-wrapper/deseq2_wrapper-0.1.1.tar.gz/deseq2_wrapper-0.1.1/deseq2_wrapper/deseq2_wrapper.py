"""
DESeq2 Python Wrapper
A Python interface for RNA-seq differential expression analysis using DESeq2 and ClusterProfiler
"""

import pandas as pd
import numpy as np
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri
from rpy2.robjects.packages import importr, isinstalled
from rpy2.robjects.conversion import localconverter
import os
import warnings
import pkg_resources
import platform

# Get the path to the R script within the package
R_SCRIPT_PATH = pkg_resources.resource_filename('deseq2_wrapper', 'deseq2_functions.R')

# Flag to track if R functions have been loaded
_R_FUNCTIONS_LOADED = False


def suppress_rtools_warnings():
    """
    Suppress Rtools PATH warnings on Windows systems.
    """
    if platform.system() == 'Windows':
        # Suppress the specific warning about PATH being redefined
        import warnings
        warnings.filterwarnings('ignore', message='.*PATH.*redefined by R.*')


def check_r_libraries():
    """
    Check if all required R libraries are installed.
    
    Returns:
        dict: Dictionary with library names as keys and installation status as values
    """
    suppress_rtools_warnings()
    
    required_libraries = ['DESeq2', 'clusterProfiler', 'org.At.tair.db', 'biomaRt']
    status = {}
    
    for lib in required_libraries:
        if isinstalled(lib):
            status[lib] = True
        else:
            status[lib] = False
            warnings.warn(f"R library '{lib}' is not installed. Please install it using R.")
    
    all_installed = all(status.values())
    if all_installed:
        print("All required R libraries are installed.")
    else:
        missing = [lib for lib, installed in status.items() if not installed]
        print(f"Missing R libraries: {', '.join(missing)}")
        print("Please install them in R using:")
        print("if (!requireNamespace('BiocManager', quietly = TRUE))")
        print("    install.packages('BiocManager')")
        for lib in missing:
            print(f"BiocManager::install('{lib}')")
    
    return status


def load_r_functions():
    """
    Load R functions from the packaged R script file.
    """
    global _R_FUNCTIONS_LOADED
    
    if _R_FUNCTIONS_LOADED:
        print("R functions already loaded.")
        return
    
    suppress_rtools_warnings()
    
    try:
        # Use forward slashes for R even on Windows
        r_script_path = R_SCRIPT_PATH.replace('\\', '/')
        ro.r(f'source("{r_script_path}")')
        _R_FUNCTIONS_LOADED = True
        print(f"R functions loaded successfully")
    except Exception as e:
        raise RuntimeError(f"Failed to load R functions: {str(e)}")


def make_dds(df_counts, meta_tags):
    """
    Create DESeq2 dataset from count matrix and metadata.
    
    Args:
        df_counts (pd.DataFrame): Count matrix with gene IDs in first column
        meta_tags (pd.DataFrame): Metadata with 'sample' column and experimental factors
        
    Returns:
        R object: DESeq2 dataset object
        
    Raises:
        ValueError: If 'sample' column is missing from metadata
        RuntimeError: If R function execution fails
    """
    if not _R_FUNCTIONS_LOADED:
        raise RuntimeError("R functions not loaded. Please call initialize() first.")
    
    try:
        # Validate metadata structure
        if 'sample' not in meta_tags.columns:
            raise ValueError("'sample' column is missing from metadata. This column is required for sample identification.")
        
        # Convert to R dataframes using the modern conversion context
        with localconverter(ro.default_converter + pandas2ri.converter):
            r_df_counts = ro.conversion.py2rpy(df_counts)
            r_meta_tags = ro.conversion.py2rpy(meta_tags)
        
        # Call R function
        r_make_dds = ro.r['make_dds']
        dds = r_make_dds(r_df_counts, r_meta_tags)
        
        print("DESeq2 dataset created successfully")
        return dds
        
    except Exception as e:
        raise RuntimeError(f"Error in make_dds: {str(e)}")


def compare_filter_annot(dds, grouping_var_name, group_test, group_base, treatment,
                        min_baseMean_threshold=10, max_padj_threshold=0.05, min_log2FC_threshold=1,
                        write_df=False):
    """
    Perform differential expression analysis with filtering and annotation.
    
    Args:
        dds: DESeq2 dataset object
        grouping_var_name (str): Name of grouping variable
        group_test (str): Test group name
        group_base (str): Control/base group name
        treatment (str): Treatment description
        min_baseMean_threshold (float): Minimum base mean expression (default: 10)
        max_padj_threshold (float): Maximum adjusted p-value (default: 0.05)
        min_log2FC_threshold (float): Minimum absolute log2 fold change (default: 1)
        write_df (bool): Whether to write results to Excel file
        
    Returns:
        pd.DataFrame: Filtered and annotated differential expression results
        
    Raises:
        RuntimeError: If R function execution fails
    """
    if not _R_FUNCTIONS_LOADED:
        raise RuntimeError("R functions not loaded. Please call initialize() first.")
    
    try:
        # Call R function with mapped parameter names
        r_compare_filter_annot = ro.r['compare_filter_annot']
        r_df_deg = r_compare_filter_annot(
            dds, 
            grouping_var_name, 
            group_test, 
            group_base, 
            treatment,
            min_baseMean_threshold,  # Maps to baseMean_threshold in R
            max_padj_threshold,      # Maps to padj_threshold in R
            min_log2FC_threshold     # Maps to log2FC_threshold in R
        )
        
        # Convert R dataframe to pandas
        with localconverter(ro.default_converter + pandas2ri.converter):
            df_deg = ro.conversion.rpy2py(r_df_deg)
        
        # Write to Excel if requested
        if write_df:
            file_name = f'df_deg_{group_test}_vs_{group_base}.xlsx'
            df_deg.to_excel(file_name, index=False)
            print(f"Results written to {file_name}")
        
        print(f"Found {len(df_deg)} differentially expressed genes")
        return df_deg
        
    except Exception as e:
        raise RuntimeError(f"Error in compare_filter_annot: {str(e)}")


def GO_from_DEGs(df_deg, write_df=False):
    """
    Perform GO enrichment analysis on differentially expressed genes.
    
    Args:
        df_deg (pd.DataFrame): Differential expression results from compare_filter_annot
        write_df (bool): Whether to write results to Excel file
        
    Returns:
        pd.DataFrame: GO enrichment results with EPRN/EPRI metrics
        
    Raises:
        RuntimeError: If R function execution fails
    """
    if not _R_FUNCTIONS_LOADED:
        raise RuntimeError("R functions not loaded. Please call initialize() first.")
    
    try:
        # Convert pandas dataframe to R
        with localconverter(ro.default_converter + pandas2ri.converter):
            r_df_deg = ro.conversion.py2rpy(df_deg)
        
        # Call R function
        r_GO_from_DEGs = ro.r['GO_from_DEGs']
        r_GO = r_GO_from_DEGs(r_df_deg)
        
        # Convert R dataframe to pandas
        with localconverter(ro.default_converter + pandas2ri.converter):
            GO = ro.conversion.rpy2py(r_GO)
        
        # Check if results are empty
        if GO.empty:
            print("No significant GO terms found")
            return GO
        
        # Write to Excel if requested
        if write_df:
            # Extract group names for file naming
            group_test = df_deg['group_test'].iloc[0]
            group_base = df_deg['group_base'].iloc[0]
            file_name = f'GO_df_deg_{group_test}_vs_{group_base}.xlsx'
            GO.to_excel(file_name, index=False)
            print(f"GO results written to {file_name}")
        
        print(f"Found {len(GO)} enriched GO terms")
        return GO
        
    except Exception as e:
        raise RuntimeError(f"Error in GO_from_DEGs: {str(e)}")


def initialize():
    """
    Initialize the DESeq2 wrapper by loading R functions.
    This should be called before using any analysis functions.
    """
    suppress_rtools_warnings()
    lib_status = check_r_libraries()
    if all(lib_status.values()):
        load_r_functions()
        return True
    else:
        warnings.warn("Some R libraries are missing. Please install them before using this package.")
        return False