import os
import pandas as pd
# from configuration import ROOT_DIR
from input.LOG_UNITS import LOG_NAMES_UNITS_DICT
from input.configuration import INPUT_DIR

"""
Clean up negative values and NaN entries for csv or excel files in input/raw directory
"""

RAW_INPUT_DIR = os.sep.join((INPUT_DIR, 'raw'))
OUTPUT_DIR = os.sep.join((INPUT_DIR, 'cleaned_up'))
OUTPUT_EXT = ''


def clean_up_df(orig_df, strict_remove=True, APIcheck=True):
    """
    Return cleaned df using numeric values only
    - Columns not defined in LOG_NAMES_UNITS_DICT are removed
    - Columns contain string entries are removed

    """

    orig_logs = set(orig_df.columns)
    API_logs = set(LOG_NAMES_UNITS_DICT)
    defined_logs = orig_logs & API_logs

    if len(defined_logs) == len(API_logs):
        print('Your inputs follow API for this project.')

    check_logs = defined_logs if strict_remove else orig_logs

    new_logs = dict()
    for new_log in set.union(check_logs, orig_logs):
        # print('doing stuff with ', new_log)
        if new_log in API_logs:     # if in API
            # print('%s is in API' % new_log)
            new_logs[new_log] = new_log + ',' + LOG_NAMES_UNITS_DICT[new_log]
        else:                       # if not in API
            if APIcheck:
                print('WARNING: %s not in API. ' % new_log)
            if strict_remove:
                print('It will be removed with strict_remove=True. To keep this column,'
                      'set strict_remove=False.')
                # remove log not defined by API
                orig_df = orig_df.drop(columns=new_log)
                # print('after remove', orig_df.columns)
            else:
                # keep the original log
                new_logs[new_log] = new_log

    # rename under new_logs
    orig_df = orig_df.rename(columns=new_logs)


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

    if len(df_cleaned) == 0:
        print('WARNING: all entries are neglected. Check this file.'
              'It is potentially that there are no row that contains all entries.')

    return df_cleaned


def clean_up(savefile=True, strict_remove=True, isfollowingAPI=True):

    # grab all well names in raw dir
    for file_name in os.listdir(RAW_INPUT_DIR):

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
        df = file_reader(os.path.join(RAW_INPUT_DIR, file_name))

        # clean up file
        df_cleaned = clean_up_df(df, strict_remove=strict_remove)
        print('Finished cleaning up.')

        if savefile:
            # save the cleaned file
            cleaned_file_name = '.'.join((well_name+OUTPUT_EXT, file_ext))
            # save file into OUTPUT_DIR
            if file_ext == 'csv':
                df_cleaned.to_csv(os.path.join(OUTPUT_DIR, cleaned_file_name))
            elif file_ext == 'xlsx':
                df_cleaned.to_excel(os.path.join(OUTPUT_DIR, cleaned_file_name))

            print('Finish saving.')

        print(df_cleaned.head())

        print('#'*100)


if __name__ == '__main__':
    clean_up(savefile=True, strict_remove=True)

    # import pandas as pd
    # import numpy as np
    # from input.LOG_UNITS import LOG_NAMES_UNITS_DICT
    #
    # print(LOG_NAMES_UNITS_DICT)
    # row = np.array(['test'])






