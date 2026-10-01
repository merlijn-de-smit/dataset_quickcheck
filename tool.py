import streamlit as st
import pandas as pd
import csv
import os
import io
import numpy as np
import datetime
import tempfile

if 'stage' not in st.session_state:
    st.session_state.stage = 0
def set_stage(stage):
    st.session_state.stage = stage
    
st.write("**Dataset Quickcheck Tool**")
st.write("--")
st.write("This script will perform some quick checks on a .csv file in order to identify possible errors. It will **not** modify your file or correct any errors. You will have to do that with a real computer program.")
st.write("--")
st.write("Merlijn de Smit, 2026 merlijn.de.smit@su.se")
st.write("--")

placeholder=st.empty()

#User uploads a file, file and path are stored as temporary files
#The tempfile functions serve no purpose at the moment, maybe later
with placeholder.container():
    actualcsv=st.file_uploader("Choose a CSV file", type="csv")
    if actualcsv:
        filename=actualcsv.name
        temp_dir = tempfile.mkdtemp()
        path = os.path.join(temp_dir, filename)
        with open(path, "wb") as f:
                f.write(actualcsv.getvalue())
    st.button("Upload this file", on_click=set_stage, args=(1,))

#Determine separator. Comma is the default value. Otherwise, accept tab or any other separator. 
    if st.session_state.stage > 0:
        separator=st.text_input("Default separator is comma. Does your file use another separator? If so, input it here. For tab, write 'tab'. Otherwise, leave blank.")
        st.button("Send answer", on_click=set_stage, args=(2,))
    
    if st.session_state.stage > 1:
        if separator=="tab":
            df=pd.read_csv(actualcsv, sep="\t")
        elif len(separator)>0:
            df=pd.read_csv(actualcsv, sep=separator)
        else:
            df=pd.read_csv(actualcsv)
        columnnames=list(df.columns.values)
        df.replace('', np.nan, inplace=True)
        emptylist = df.index[df.isna().all(axis=1)].tolist()
        df.dropna(how='all', inplace=True)
        st.write("File loaded correctly!")
        st.write("Column names are:")
        for column in columnnames:
            st.write(column)
    #Date/time column needs to be identified separately in order to process it by lowest and highest values. 
        datetimecol=st.text_input("Does the dataset contain a column with a date/time value? If so, enter its name here. Otherwise, write 'no'.")
    #Identifier column is identified separately in order to display a warning message if the column contains non-unique values
        identifycol=st.text_input("Does the dataset contain a column that uniquely identifies each observation? If so, enter its name here. It may be the same as the date/time value, or another ID. Otherwise, write 'no'.")
        if st.button("Continue", on_click=set_stage, args=(3,)):
            placeholder.empty()

#Initialize sidebar
if st.session_state.stage > 2:
    emptyrows=st.sidebar.button("Check for empty rows")
    mixedvalues=st.sidebar.button("Check for mixed data types")
    duplicates=st.sidebar.button("Check for duplicates")
    unique=st.sidebar.button("Check for unique values")
    outliers=st.sidebar.button("Check for outliers")
    export=st.sidebar.button("Export a codebook file")
    
    st.write("Working with file:", filename)
    st.write("--")
    st.write("Please choose an option from the left sidebar")

    if emptyrows:
        placeholder.empty()
        if len(emptylist)>0:
            st.write("**Warning:** there are rows in the dataset that appear to be empty!")
            st.write("Row numbers of empty rows (starting from zero):")
            for item in emptylist:
                st.write(item)
        else:
            st.write("No empty rows found in dataset!")

    if mixedvalues:
        placeholder.empty()
        buffer=io.StringIO()
        df.info(buf=buffer, verbose=True, show_counts=True)
        #s=buffer.getvalue()
        #st.text(s)
        #st.write("--")
        st.write("**Checking for mixed values in columns:**")
        st.write("The value 'mixed' may or may not indicate a problem. Check this manually.")
        for column in df.columns:
            st.write(column,':',pd.api.types.infer_dtype(df[column]))
        
#Script to check for duplicates
    if duplicates:
        placeholder.empty()
        st.write("This will check for duplicate rows including timestamp and identifier colums. Duplicates therefore almost always indicate a problem.")
        duplicates=df[df.duplicated()]
        if len(duplicates):
            st.write("Duplicate rows found in dataset!")
            st.write("Duplicates found:", duplicates)
        else:
            st.write("No duplicate rows in dataset!")
        
#Check for the proportion of unique values in each column. The script will report if there are no unique values (empty column), if an identifying column has non-unique values (likely duplicate row)
#and if the proportion of unique values is very high but not 100% (this is often not an error but may indicate one if the column is meant to be identifying).
    if unique:
        placeholder.empty()
        st.write("This will count the number of unique values in each column. It should be maximum for identifying columns (ID, timestamp), high for columns with precise numeric values, low for columns with ordinal or categorical values")
        for column in df:
            unique_count=df[column].nunique()
            total_rows=df[column].count()
            percentage=(100/total_rows)*unique_count
            st.write(column, "has", unique_count, "unique values over a total of", total_rows, "non-null rows")
            if unique_count==0:
                st.write("- **Warning**: no unique values found. Is this an empty column?")
            if column == identifycol and percentage < 100:
                st.write("- **Warning**: non-unique values in identifying column! Please check this.")
            if percentage > 98 and percentage < 100 and column != identifycol:
                st.write("- **Warning**: more than 98% (but less than 100%) of values are unique. Is this an identifying column with errors?")

#The script will first simply output the heads (lowest five values) and tails (highest five values) of sorted columns, after filtering for numeric. Then, a calculation is performed on whether the highest/lowest value is
#lower than the average of the four nearest values by a factor of five. A warning message is then displayed.
#In order to reliably report this result with series of negative numbers, negative numbers are temporarily treated as positives with the abs() function.
#The script will likely not perform well with series that combine positive and negative numbers, but this needs to be tested.
#Script will display a warning message only if the total number of values in a column exceeds five (if the number of values is very small, it makes little sense to identify "outliers".
#The code here is probably unnecessarily complicated and verbose, needs to be simplified and slimmed down later if possible.
    if outliers:
        placeholder.empty()
        st.write("This outputs the five highest and five lowest values per column. If a maximum/minimum value is MUCH higher or lower than the adjacent one, this may indicate a data entry problem (misplaced comma or the like)")
        st.write("--")
        st.write("This should ignore most common notations of NaN values. If your dataset contains eccentric ways of denoting NaN, it will affect the output - but this is something you want to check anyway!")
        st.write("--")
        st.write("The script will try to treat all data types as numeric. If this is not possible, for example because the data type is not a number, the output will be 'none'")
        st.write("--")
        df.replace(np.nan, '', regex=True, inplace=True)
        df.replace('NAN','', inplace=True)
    #df=df.astype(str)
        for column in df:
            sortdf=df[df[column]!=""]
            if column!=datetimecol:
                sortdf[column]=pd.to_numeric(sortdf[column], errors='coerce')
            sortdf.sort_values(by=column, inplace=True, na_position = 'last', )#sorts ascending with NaN last.
            st.write("Five lowest values of", column, "are:", sortdf[column].head())
            if sortdf[column].dtype in ["int64","float64"]:
                sortlist=sortdf[column].tolist()
                if len(sortlist)>5: #Following script should not be performed if the amount of values is less than five
                    bxs=sortlist[0:5]
                #example [-5,-4,-3,-2,-1]
                    if sortlist[0]<0:
                    #true as -1<0
                        abslist=[]
                        for i in bxs:
                            abslist.append(abs(i))
                        #now: [5,4,3,2,1]
                        xs=abslist[1:5]#meaning xs is now [4,3,2,1]
                        if abslist[0]>((sum(xs)/4)*5) and abslist[0]!=0: #should not obtain as 5 is not higher than 5*average of [4,3,2,1]
                            st.write("**Warning**: lowest value is much lower than the other ones.")
                    else:
                        xs=bxs[1:5] #example [2,3,4,5] with bsx[0]=1
                        if bxs[0]<((sum(xs)/4)/5) and bxs[0]!=0: 
                            st.write("**Warning**: lowest value is much lower than the other ones.")
            sortdf.sort_values(by=column, inplace=True, na_position = 'first')
            st.write("Five highest values of", column, "are:", sortdf[column].tail())
            if sortdf[column].dtype in ["int64","float64"]:
                sortlist=sortdf[column].tolist()
                if len(sortlist)>5:
                    bxs=sortlist[-5:]
                    abslist=[]
                    if sortlist[(len(sortlist)-1)]<0:
                        for i in bxs:
                            abslist.append(abs(i))
                            xs = abslist[-5:-1]  # meaning xs is now [4,3,2,1]
                            if abslist[0] > ((sum(xs) / 4) * 5) and abslist[0] != 0:
                                st.write("**Warning**: highest value is much higher than the other ones!")
                    else:
                        xs=bxs[0:4]
                        if bxs[4]>((sum(xs)/4)*5):
                            st.write("**Warning**: highest value is much higher than the other ones.")


    if export:
        placeholder.empty()
        st.write("This will write a .txt file with information about variables and observations. You can use it to create a codebook or a data description. The file will be saved in the same location as the python tool.")
        st.write("--")
        df.replace('',np.nan, regex=True, inplace=True)
        file_path=os.path.join(path, filename)
        stat_info=os.stat(path)
        bytes_data=actualcsv.getvalue()
        file_size = len(bytes_data)
        mod_time_timestamp = stat_info.st_mtime
        mod_time = datetime.datetime.fromtimestamp(mod_time_timestamp)
        with open("codebook.txt", "w") as codebook:
            codebook.write("File name is: "+ filename+ "\n")
            codebook.write("\n")
            codebook.write(f"File Size: {file_size} bytes"+"\n")
            #Last modified at the moment returns the timestamp of the temporary file created by the script. Comment out until resolved.
            #codebook.write(f"Last Modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}"+"\n")
            #codebook.write("\n")
            codebook.write("Number of variable colums: "+str(len(columnnames))+ "\n")
            codebook.write("Number of rows: "+str(df.shape[0])+ "\n")
            codebook.write("\n")
            codebook.write("Variables:\n")
            codebook.write("\n")
            i=0
            for column in df:
                result=df[column].count()
                codebook.write("'"+columnnames[i]+"'"+ " --- Number of non-null observations: "+ str(result)+ "\n")
                i=i+1        
        st.write("--")
        st.write("**Finished**")
        
    
