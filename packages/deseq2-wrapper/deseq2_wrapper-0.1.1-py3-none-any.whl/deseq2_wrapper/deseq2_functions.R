library('DESeq2')
library("clusterProfiler")
library("org.At.tair.db")
library("biomaRt")

make_dds = function(df_counts, meta_tags){
  # Set row names from first column of count matrix
  rownames(df_counts) = df_counts[,1]
  df_counts = df_counts[,-1]
  
  # Handle metadata: set sample column as row names
  if ("sample" %in% colnames(meta_tags)) {
    rownames(meta_tags) = meta_tags$sample
    meta_tags$sample = NULL  # Remove the sample column after setting as row names
  } else {
    stop("'sample' column is required in metadata but was not found")
  }
  
  # Filter out rows with zero counts
  df_counts = df_counts[rowSums(df_counts)>0, ]
  df_counts = round(df_counts)
  
  # Ensure column names of count matrix match row names of metadata
  # This is critical for DESeq2
  if (!all(colnames(df_counts) == rownames(meta_tags))) {
    # Try to match by reordering
    if (all(colnames(df_counts) %in% rownames(meta_tags))) {
      meta_tags = meta_tags[colnames(df_counts), , drop=FALSE]
    } else {
      stop("Column names of count matrix do not match row names of metadata")
    }
  }
  
  # Create DESeq dataset
  dds = DESeqDataSetFromMatrix(countData = df_counts, 
                               colData = meta_tags, 
                               design = ~group)
  dds = DESeq(dds)
  return(dds)
}


compare_filter_annot = function(dds, grouping_var_name, group_test, group_base, treatment, 
                                baseMean_threshold = 10, padj_threshold = 0.05, 
                                log2FC_threshold = 1){
  res = results(dds, contrast = c(grouping_var_name, group_test, group_base))
  df_deg = as.data.frame(res)
  
  # Remove NA values
  df_deg = df_deg[!is.na(df_deg$padj), ]
  
  # Apply filters with parameterized thresholds
  deg_filter = (df_deg$baseMean >= baseMean_threshold) & 
               (df_deg$padj <= padj_threshold) & 
               (abs(df_deg$log2FoldChange) >= log2FC_threshold)
  df_deg = df_deg[deg_filter, ]
  
  # Add metadata columns
  df_deg$gene_id = rownames(df_deg)
  df_deg$group_test = group_test
  df_deg$group_base = group_base
  df_deg$treatment = treatment
  df_deg$trend = ''
  df_deg[df_deg$log2FoldChange > 0, ]$trend = 'up'
  df_deg[df_deg$log2FoldChange < 0, ]$trend = 'down'
  
  # Get annotations from BioMart
  tair_mart = useMart(biomart = 'plants_mart',
                      host = 'plants.ensembl.org', 
                      dataset = 'athaliana_eg_gene')
  
  annot = getBM(mart = tair_mart,
                attributes = c('ensembl_gene_id', 'entrezgene_id', 'description', 'external_gene_name'),
                filters = 'ensembl_gene_id',
                values = df_deg$gene_id,
                uniqueRows = FALSE)
  annot$gene_id = annot$ensembl_gene_id
  annot = annot[!duplicated(annot$gene_id), ]
  
  # Merge annotations with DEG results
  df_deg = merge(x = df_deg, y = annot, by = 'gene_id', all.x = TRUE)
  
  # Handle NA values in annotation columns before type conversion
  # Replace NA values with "NA" string first
  df_deg$ensembl_gene_id[is.na(df_deg$ensembl_gene_id)] = "NA"
  df_deg$description[is.na(df_deg$description)] = "NA"
  df_deg$external_gene_name[is.na(df_deg$external_gene_name)] = "NA"
  
  # Ensure columns are character type
  df_deg$ensembl_gene_id = as.character(df_deg$ensembl_gene_id)
  df_deg$description = as.character(df_deg$description)
  df_deg$external_gene_name = as.character(df_deg$external_gene_name)
  
  return(df_deg)
}

GO_from_DEGs = function(df_deg){
  deg_list = df_deg$gene_id
  
  # Perform GO enrichment analysis
  GO = enrichGO(gene = deg_list,
                keyType = 'TAIR',
                OrgDb = "org.At.tair.db",
                ont = 'ALL')
  GO = as.data.frame(GO)
  
  # Return empty dataframe if no enrichment found
  if (nrow(GO) == 0) {return(GO)}
  
  # Add metadata columns
  GO$group_base = df_deg$group_base[1]
  GO$group_test = df_deg$group_test[1]
  GO$treatment = df_deg$treatment[1]
  GO$gene_count_bg = 0
  GO$ref_eprn = 0
  GO$eprn = 0
  
  # Calculate EPRN metrics
  for (i in 1:nrow(GO)){
    GO[i,]$gene_count_bg = as.numeric(unlist(strsplit(GO[i,]$BgRatio, split = "/"))[1])
    GO[i,]$ref_eprn = GO[i,]$gene_count_bg^0.5
    current_gene_list = unlist(strsplit(GO[i,]$geneID, split = '/'))
    temp = df_deg[df_deg$gene_id %in% current_gene_list, ]
    GO[i,]$eprn = sum(temp$log2FoldChange^2)^0.5
  }
  
  # Calculate EPRI (Euclidean Pathway Regulation Index)
  GO$epri = GO$eprn/GO$ref_eprn
  
  return(GO)
}