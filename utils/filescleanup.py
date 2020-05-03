import os
import pandas as pd
from configuration import ROOT_DIR

"""
Clean up negative values and NaN entries for csv or excel files in input/raw directory
"""

INPUT_DIR = os.sep.join((ROOT_DIR, 'input', 'raw'))
OUTPUT_DIR = os.sep.join((ROOT_DIR, 'input', 'cleaned_up'))
OUTPUT_EXT = '_cleaned_up'


def clean_up_df(orig_df, keep_TVD=False):
    """Return cleaned df using numeric values only
    So if the columns contain string entries, they are not accounted for
        when """

    # strip-off
    if not keep_TVD:
        orig_df = orig_df.drop(columns='True Vertical Depth')

    # strip-off NaN entries
    new_df = orig_df.dropna()

    # only use numeric entries
    numeric_df = new_df._get_numeric_data().values
    # positive logs values are filtered
    masked_rows = numeric_df > 0
    # only rows that satisfy True in all columns are selected
    rows_location = masked_rows.all(axis=1)

    # cleaned df based on rows_location
    df_cleaned = orig_df[rows_location]
    if len(df_cleaned) == 0: print('Warning: all entries are neglected. Check this file.')
    print(df_cleaned.head())
    return df_cleaned


def clean_up():
    # grab all well names in raw dir
    for file_name in os.listdir(INPUT_DIR):

        # grab well name and file extension
        well_name, file_ext = os.path.splitext(file_name)
        file_ext = file_ext[1:] # ignore . before extension

        # reader based on extension
        if file_ext == 'csv':
            file_reader = pd.read_csv
        elif file_ext == 'xlsx':
            file_reader = pd.read_excel
        else: # if not either one of them, they are not data files
            continue

        print('Cleaning %s.' % file_name)
        df = file_reader(os.path.join(INPUT_DIR, file_name))

        # clean up file
        df_cleaned = clean_up_df(df)
        print('Finished cleaning up.')
        # save the cleaned file
        cleaned_file_name = '.'.join((well_name+OUTPUT_EXT, file_ext))
        # save file into OUTPUT_DIR
        if file_ext == 'csv':
            df_cleaned.to_csv(os.path.join(OUTPUT_DIR, cleaned_file_name))
        elif file_ext == 'xlsx':
            df_cleaned.to_excel(os.path.join(OUTPUT_DIR, cleaned_file_name))

        print('Finish saving.')
        print('='*100)


if __name__ == '__main__':
    clean_up()







