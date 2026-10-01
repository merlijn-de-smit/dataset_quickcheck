# dataset\_quickcheck

**Dataset Quickcheck Tool**. A Python tool intended for quickly look for common errors in large numeric datasets.

It is not intended as a replacement for real software such as OpenRefine, but intended for quickly checking for common errors for example when preparing a dataset for publication under time pressure.

The tool can take any separated values file (.csv, .tsv) as input and will identify issues such as empty rows, duplicate rows, suspicious numbers of unique or non-unique values, as well as outliers that may indicate data entry errors.

The tool is also able to output information on variables, number of observations, file size and the like to a .txt file that can be used as a basis for a readme or a codebook file.

**Requirements**: You will need Python, as well as the following modules:

streamlit
pandas
csv
os
io
numpy

datetime

**Installation**:

Extract the directory wherever you want.

Navigate to it in PowerShell/Terminal, start with "streamlit run tool.py".

Upload a .csv file.

You will be able to specify any separator, including tab, while loading the file.

**Disclaimer**:

The code looks like a jerry-rigged mess. But it sort of works.

