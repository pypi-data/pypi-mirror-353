# DESeq2 Python Wrapper

A Python interface for RNA-seq differential expression analysis using DESeq2 and ClusterProfiler, specifically designed for Arabidopsis thaliana research.

## Overview

This package provides a seamless Python interface to R's DESeq2 and ClusterProfiler packages, enabling differential expression analysis and GO enrichment analysis within Python workflows. The wrapper handles all data type conversions between Python and R, ensuring compatibility and ease of use.

## Installation

### Prerequisites

Before installing this package, ensure you have R installed with the following Bioconductor packages:

```R
if (!requireNamespace("BiocManager", quietly = TRUE))
    install.packages("BiocManager")

BiocManager::install(c("DESeq2", "clusterProfiler", "org.At.tair.db", "biomaRt"))
```

### Install from PyPI

```bash
pip install deseq2-wrapper
```

### Install from Source

```bash
git clone https://github.com/yourusername/deseq2-wrapper.git
cd deseq2-wrapper
pip install .
```

## Usage

### Basic Workflow

```python
import pandas as pd
from deseq2_wrapper import initialize, make_dds, compare_filter_annot, GO_from_DEGs
IMPORTANT NOTE: the first import of deseq2_wrapper library may fail due to stupid Rtools bugs. Repeat it 1-2 times and it will automatically work and I don't know why.

# Initialize the package (required before first use)
initialize()

# Load your data
df_counts = pd.read_excel("normalized_count.xlsx")
meta_tags = pd.read_excel("metadata.xlsx")

# Create DESeq2 dataset
dds = make_dds(df_counts, meta_tags)

# Perform differential expression analysis
df_deg = compare_filter_annot(
    dds, 
    grouping_var_name="group",
    group_test="treated", 
    group_base="control", 
    treatment="drug_treatment",
    min_baseMean_threshold=10,
    max_padj_threshold=0.05,
    min_log2FC_threshold=1,
    write_df=True
)

# Perform GO enrichment analysis
GO_results = GO_from_DEGs(df_deg, write_df=True)
```

### Data Format Requirements

**Count Matrix Format:**
- First column: Gene IDs
- Subsequent columns: Sample expression counts
- Column names must match sample names in metadata

**Metadata Format:**
- Must contain a 'sample' column with sample names matching count matrix columns
- Must contain a 'group' column defining experimental conditions
- Additional columns can include other experimental factors

## Features

- **Differential Expression Analysis**: Identifies significantly regulated genes using DESeq2
- **GO Enrichment Analysis**: Performs Gene Ontology enrichment with EPRN/EPRI metrics
- **BioMart Integration**: Automatically annotates genes with descriptions and symbols
- **Excel Integration**: Reads input from and writes results to Excel files
- **Comprehensive Error Handling**: Provides clear error messages for troubleshooting

## Functions

### check_r_libraries()
Verifies that all required R packages are installed and provides installation instructions if needed.

### make_dds(df_counts, meta_tags)
Creates a DESeq2 dataset from count matrix and metadata.

### compare_filter_annot(dds, grouping_var_name, group_test, group_base, treatment, ...)
Performs differential expression analysis with customizable filtering thresholds.

### GO_from_DEGs(df_deg, write_df=False)
Performs GO enrichment analysis on differentially expressed genes.

## Output Files

The package generates Excel files with standardized naming conventions:
- Differential expression results: `df_deg_{group_test}_vs_{group_base}.xlsx`
- GO enrichment results: `GO_df_deg_{group_test}_vs_{group_base}.xlsx`

## Citation

If you use this package in your research, please cite:
- DESeq2: Love MI, Huber W, Anders S (2014). Genome Biology
- clusterProfiler: Yu G, et al. (2012). OMICS: A Journal of Integrative Biology

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Known Issues and Troubleshooting

### Windows Users
On Windows systems with Rtools installed, you may see warnings about PATH being redefined. These warnings are harmless and can be ignored. The package automatically suppresses these warnings.

If you encounter "access violation" errors on import, ensure you're calling `initialize()` manually after importing rather than letting it run automatically.

### Initialization Required
Starting from version 0.1.0, you must call `initialize()` before using any analysis functions. This prevents conflicts on some systems:

```python
from deseq2_wrapper import initialize
initialize()  # Call this once before using other functions
```

## Support

For issues and questions, please use the GitHub issue tracker.