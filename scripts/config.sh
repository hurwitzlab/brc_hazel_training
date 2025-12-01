export ID=MY_ID
export IN_LIST="/your/path/to/repo/sample_list.txt"  # Path to the SRA accessions file
export IN_DIR="/path/to/raw_reads"                                                      # Directory containing raw reads
export FASTQC_SIF="/path/to/container/image"                                             # Path to the FastQC container

# Create output directory if it doesn't exist
mkdir -p /path/to/working/dir/01_raw_fastqc_results
export OUT_DIR="/path/to/working/dir/01_raw_fastqc_results"