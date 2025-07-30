# AnnoSINE

SINE Annotation Tool for Plant Genomes

# Table of Contents
- [Introduction](#Introduction)
- [Prerequisites](#Prerequisites)
- [Installation](#Installation)
- [Usage](#Usage)
- * [Argument](#Argument)
- * [Inputs](#Inputs)
- * [Outputs](#Outputs)
- * [Testing](#Testing)
- [Citations](#Citations)

# Introduction
AnnoSINE is a SINE annotation tool for plant genomes. The program is designed to generate high-quality non-redundant SINE libraries for genome annotation. It uses the manually curated SINE library in the *Oryza sativa* genome to benchmark the annotation performance.

<div  align="center">   
<img src="https://github.com/yangli557/AnnoSINE/blob/main/pipeline.png" width = "700" height = "900" />
</div>

<!AnnoSINE has eight major modules. The first one is to identify putative SINE candidates by applying hidden Markov model (HMM)-based homology search, structure-based *de novo* search or combinition of homology-structure-based search. This step is usually sensitive but can output many false SINE candidates. In the 2nd step, it searches for target site duplication (TSD) in the flanking region to further verify each SINE candidate. As TSD is a significant feature of SINEs, this step is highly effective in removing non-SINEs. Although searching for TSD can be conducted in the later stage of the pipeline, removing false positives earlier can save the computational time of the downstream analysis. In the 3rd step, it examines the copy number and the alignment of SINE copies to remove the sequences with few copy numbers or shifted/fragmented/extended alignments. In addition, it can identify some lineage-specific differences, such as the length of the 3' end using the alignment profile. In the 4th step, it decides the superfamily of each candidate SINE sequence and remove highly similar candidates from known non-coding RNAs. Meanwhile, the highly identical sequences assembling to RNA are false positives. In the 5th step, it removes candidates with a large proportion of tandem repeats. In the 6th step, it removes other TEs by detecting inverted repeats adjacent to TSDs. These steps focused on identifying complete SINEs (i.e., *seed sequences*) in the query genome. Redundant seeds are filtered to generate the SINE library. After we obtain the non-redundant seed sequences, it will apply RepeatMasker to identify other SINEs to complete the whole genome SINE annotation in the last step.-->

# Prerequisites
To use AnnoSINE, you need to install the tools listed below.

 - [Python 3.7.4](https://www.python.org/)
 - [HMMER 3.3.1](http://hmmer.org/download.html)
 - [BLAST+ 2.10.1](https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/2.10.1/)
 - [TRF 4.09](https://tandem.bu.edu/trf/trf.download.html)
 - [IRF 3.0X](https://tandem.bu.edu/irf/irf.download.html)
 - [CD-HIT 4.8.1](https://github.com/weizhongli/cdhit/releases/download/V4.8.1/cd-hit-v4.8.1-2019-0228.tar.gz)
 - [RepeatMasker 4.1.2](http://www.repeatmasker.org/RepeatMasker/)
 - [Node 12.18.2](https://nodejs.org/en/download/)

# Installation

```
# pip
cd ./AnnoSINE/bin
pip3 install -r requirements.txt

# conda
conda env create -f AnnoSINE.conda.yaml

## change the permission of IRF
chmod 755 irf308.linux.exe
```

# Usage

```
conda activate AnnoSINE
python3 AnnoSINE.py [options] <mode> <input_filename> <output_filename>
```
If the program stops in a certain step or has no output, this may result from the strict filtering cutoff. You can try the command below:
```
python3 AnnoSINE.py [options] <mode> -e 0.01 -minc 1 -s 150 <input_filename> <output_filename>
```

## Argument
```
positional arguments:
  mode                  [1 | 2 | 3]
                        Choose the running mode of the program.
                                1--Homology-based method;
                                2--Structure-based method;
                                3--Hybrid of homology-based and structure-based method.
  input_filename        input genome assembly path
  output_filename       output files path

optional arguments:
  -h, --help                   show this help message and exit
  -e, --hmmer_evalue           Expectation value threshold for saving hits of homology search (default: 1e-10)
  -v, --blast_evalue           Expectation value threshold for sequences alignment search (default: 1e-10)
  -l, --length_factor          Threshold of the local alignment length relative to the the BLAST query length (default: 0.3)
  -c, --copy_number_factor     Threshold of the copy number that determines the SINE boundary (default: 0.15)
  -s, --shift                  Maximum threshold of the boundary shift (default: 80)
  -g, --gap                    Maximum threshold of the trancated gap (default: 10)
  -minc, --copy_number         Minimum threshold of the copy number for each element (default: 20)
  -a, --animal                 If set to 1, then Hmmer will search SINE using the animal hmm files from Dfam. (default: 0)
  -b, --boundary               Output SINE seed boundaries based on TSD or MSA (default: msa)
  -f, --figure                 Output the SINE seed MSA figures and copy number profiles (y/n). Please note that this step may take a long time to process. (default: n)  
  -auto, --automatically_continue If set to 1, then the program will skip finished steps and continue unifinished steps for a previously processed output dir. (default: 0)
  -r, --non_redundant          Annotate SINE in the whole genome based on the non—redundant library (y/n) (default: y)
  -t, --threads		              Threads for each tool in AnnoSINE (default: 36)
  -irf, --irf_path	            Path to the irf program (default: '')
  -rpm, --RepeatMasker_enable  If set to 0, then will not run RepearMasker (Step 8 for the code). (default: 1)
```

## Inputs
Genome sequence(fasta format).

## Outputs
- Redundant SINE library: $ Step7_cluster_output.fasta
- Non-redundant SINE library with serial number: $Seed_SINE.fa.
- Whole-genome SINE annotation: $Input_genome.fasta.out. This file contains high-similarity SINE annotations.

## Intermediate Files
- SINE candidates information predicted by homology search: $ ../Family_Seq/Family_Name/Family_Name.out. (m=1 or 3 required)
- SINE candidate sequences predicted by structure search: $ ../Input_Files/Input_genome-matches.fasta. (m=2 or 3 required)
- Extended candidate sequences for TSD search: $ Step1_extend_tsd_input.fa
- TSD identification outputs: $ Step2_tsd.txt
- MSA extended input sequences flanked with TSD: $ Step2_extend_blast_input.fa
- MSA output: $ Step3_blast_output.out
- Intermediate sequences with MSA quality examination: $ Step3_blast_process_output.fa
- SINE candidate sequences after MSA quality examination: $ Step4_rna_input.fasta
- SINE candidates blast against RNA database outputs $ Step4_rna_output.out
- Classified SINE candidates after RNA examintation $ Step4_rna_output.fasta
- TRF output $ Step4_rna_output.fasta.2.5.7.80.10.10.2000.dat
- SINE candidates after removing elements consist of tandem repeats $ Step5_trf_output.fasta
- SINE candidate sequences after extension: $ Step6_irf_input.fasta.
- IRF output $ Step6_irf_input.fasta.2.3.5.80.10.20.500000.10000.dat
- SINE candidates after removing elements flanked with inverted repeats: $ Step6_irf_output.fasta
- CD-HIT output: $ Step7_cluster_output.fasta.clstr

# Testing 
You can test the AnnoSINE with one chromosome in *Arabisopsis thaliana* (it takes about 6 mins).
```
cd ./AnnoSINE/Testing
python3 ../bin/AnnoSINE.py -t 20 3 A.thaliana_Chr4.fasta ./Output_Files
```
Results of AnnoSINE tests on testing data are saved in Output_Files.

# Citations
