# dataset_quickcheck
**Dataset Quickcheck Tool**. A Python tool intended for quickly look for common errors in large numeric datasets.

It is not intended as a replacement for real software such as OpenRefine, but intended for quickly checking for common errors for example when preparing a dataset for publication under time pressure.

The tool can take any separated values file (.csv, .tsv) as input and will identify issues such as empty rows, duplicate rows, suspicious numbers of unique or non-unique values, as well as outliers that may indicate data entry errors.

**Requirements**: You will need Python, as well as the following modules:

streamlit
pandas
csv
os
io
numpy

**Installation**:

Extract the directory wherever you want. 

Place the CSV you want to check in the "input" directory. Please have only one CSV there at a time, and do not have the file open in another program while running this. (You can however quickly open and close the file once the script has started).

You will be able to specify any separator, including tab, while loading the file.

Navigate to it in PowerShell/Terminal, start with "streamlit run tool.py".

**Disclaimer**:

The code looks like a jerry-rigged mess. But it sort of works.
