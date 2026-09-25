import streamlit as st
import pandas as pd
import csv
import os
import io
import numpy as np

if 'stage' not in st.session_state:
    st.session_state.stage = 0
def set_stage(stage):
    st.session_state.stage = stage
    
st.write("**Dataset Quickcheck Tool**")
st.write("--")
st.write("This script will perform some quick checks on a .csv file in order to identify possible errors. It will **not** modify your file or correct any errors. You will have to do that with a real computer program.")
st.write("--")
mypath=os.path.join(os.path.dirname(__file__),'input')
dirlist=os.listdir(mypath)

#Lists the files in the directory. The first one (preferably the only one) can be selected.
for item in dirlist:
    st.write("File in directory:", item)
if len(dirlist)>1:
    st.write("Multiple files in directory. You can only select the first one. You can remove the other ones and restart this app. Please make sure that the file you want to have checked is not open in another application. If so, close the application and restart this app.")
st.write("Do you want to load the first file in the list?")
st.button("Yes", on_click=set_stage, args=(1,))

#Determine separator. Comma is the default value. Otherwise, accept tab or any other separator. 
if st.session_state.stage > 0:
    separator=st.text_input("Default separator is comma. Does your file use another separator? If so, input it here. For tab, write 'tab'. Otherwise, leave blank.")
    st.button("Send answer", on_click=set_stage, args=(2,))
    
if st.session_state.stage > 1:
    actualcsv=os.path.join(os.path.dirname(__file__),'input', dirlist[0])
    if separator=="tab":
        df=pd.read_csv(actualcsv, sep="\t")
    elif len(separator)>0:
        df=pd.read_csv(actualcsv, sep=separator)
    else:
        df=pd.read_csv(actualcsv)
    columnnames=list(df.columns.values)
    st.write("File loaded correctly!")
    st.write("Column names are:", columnnames)
    #Date/time column needs to be identified separately in order to process it by lowest and highest values. 
    datetimecol=st.text_input("Does the dataset contain a column with a date/time value? If so, enter its name here. Otherwise, write 'no'.")
    #Identifier column is identified separately in order to display a warning message if the column contains non-unique values
    identifycol=st.text_input("Does the dataset contain a column that uniquely identifies each observation? If so, enter its name here. It may be the same as the date/time value, or another ID. Otherwise, write 'no'.")
    st.button("Continue", on_click=set_stage, args=(3,))

#Check for rows that are completely empty, and then drop them from the temporary dataframe.
if st.session_state.stage > 2:
    df.replace('', np.nan, inplace=True)
    emptylist = df.index[df.isna().all(axis=1)].tolist()
    df.dropna(how='all', inplace=True)
    if len(emptylist)>0:
        st.write("**Warning:** there are rows in the dataset that appear to be empty!")
        st.write("Row numbers of empty rows (starting from zero):")
        for item in emptylist:
            st.write(item)
    st.button("**Get dataset summary**", on_click=set_stage, args=(4,))

if st.session_state.stage > 3:
    buffer=io.StringIO()
    df.info(buf=buffer, verbose=True, show_counts=True)
    s=buffer.getvalue()
    st.text(s)
    st.write("--")
    st.write("**Checking for mixed values in columns:**")
    st.write("The value 'mixed' may or may not indicate a problem. Check this manually.")
    for column in df.columns:
        st.write(column,':',pd.api.types.infer_dtype(df[column]))
        

    st.button("**Check for duplicate rows**", on_click=set_stage, args=(5,))
    st.write("This will check for duplicate rows including timestamp and identifier colums. Duplicates therefore almost always indicate a problem.")

#Script to check for duplicates
if st.session_state.stage > 4:
    duplicates=df[df.duplicated()]
    if len(duplicates):
        st.write("Duplicate rows found in dataset!")
        st.write("Duplicates found:", duplicates)
    else:
        st.write("No duplicate rows in dataset!")
        
    st.button("**Check for unique values**", on_click=set_stage, args=(6,))
    st.write("This will count the number of unique values in each column. It should be maximum for identifying columns (ID, timestamp), high for columns with precise numeric values, low for columns with ordinal or categorical values")

#Check for the proportion of unique values in each column. The script will report if there are no unique values (empty column), if an identifying column has non-unique values (likely duplicate row)
#and if the proportion of unique values is very high but not 100% (this is often not an error but may indicate one if the column is meant to be identifying).
if st.session_state.stage > 5:
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

    st.button("**Check for highest and lowest values per column**", on_click=set_stage, args=(7,))
    st.write("This outputs the five highest and five lowest values per column. If a maximum/minimum value is MUCH higher or lower than the adjacent one, this may indicate a data entry problem (misplaced comma or the like)")
    st.write("--")
    st.write("This should ignore most common notations of NaN values. If your dataset contains eccentric ways of denoting NaN, it will affect the output - but this is something you want to check anyway!")
    st.write("--")
    st.write("The script will try to treat all data types as numeric. If this is not possible, for example because the data type is not a number, the output will be 'none'")
    st.write("--")

#The script will first simply output the heads (lowest five values) and tails (highest five values) of sorted columns, after filtering for numeric. Then, a calculation is performed on whether the highest/lowest value is
#lower than the average of the four nearest values by a factor of five. A warning message is then displayed.
#In order to reliably report this result with series of negative numbers, negative numbers are temporarily treated as positives with the abs() function.
#The script will likely not perform well with series that combine positive and negative numbers, but this needs to be tested.
#Script will display a warning message only if the total number of values in a column exceeds five (if the number of values is very small, it makes little sense to identify "outliers".
#The code here is probably unnecessarily complicated and verbose, needs to be simplified and slimmed down later if possible.
if st.session_state.stage > 6:
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
        st.write("--")
    st.write("**Finished**")
        
    
