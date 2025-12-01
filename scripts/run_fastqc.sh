#! /bin/bash
# This script submits a job array on an LSF scheduler to run FastQC on raw reads
# Each job array will process multiple samples in parallel
# The number of samples is determined by the number of lines in the input list file     
# --------------------------------------------------


# load job configuration
source ./config.sh


# make sure sample file is in the right place
if [[ ! -f "$IN_LIST" ]]; then
    echo "$IN_LIST does not exist. Please provide the path for a list of datasets to process. Job terminated."
    exit 1
fi

export JOB1="fastqc"  # this is not necessary but will be useful for consistency in larger pipelines

# get number of samples to process
# the number of samples will be used to set the range of the job array
export NUM_JOB=$(wc -l < "$IN_LIST")

# submit job arrays for each step
echo "launching ${JOB1}.lsf as a job."
JOB_ID=`bsub -J "$JOB1[1-$NUM_JOB]%$NUM_JOB" < ${JOB1}.lsf`