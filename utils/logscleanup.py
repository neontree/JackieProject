
from collections import OrderedDict

import numpy as np

"""
Utilities to extract and clean up LAS files
"""


def get_specific_attr_mapping(las_file_loc):
    """Mapping of attr name to attr idx and attr units
    This is specific to each LAS file, thus changing it if needed
    Specify the logs that you need to extract only, and their units"""

    def _get_mapping(logs_names, logs_names_col_idx, logs_units):
        attr_mapping_idx = OrderedDict()
        attr_mapping_unit = OrderedDict()
        for log_name, log_col_idx, log_unit in zip(logs_names, logs_names_col_idx, logs_units):
            attr_mapping_idx[log_name] = log_col_idx
            attr_mapping_unit[log_name] = log_unit

        return attr_mapping_idx, attr_mapping_unit

    # Assuming the LAS file is on the same directory
    if las_file_loc == r'../input_template/Middleton Unit B 47-38 No. 8SH__From EDR.las':
        # row where the log reading starts
        # specific to each LAS file
        row_idx_start = 47
        # col where the required log are and their units
        # specific to each LAS file
        logs_names = ['TVD', 'ROP', 'RPM', 'TOR', 'WOB', 'DIFP']
        logs_names_col_idx = [0, 2, 3, 4, 5, 9]
        logs_units = ['ft', 'ft/hr', 'rev/min', 'in/lb', 'kDaN', 'kPa']

    elif las_file_loc == r'../input_template/LAS Middleton Unit B 47-38 No. 8SH_From MWD.las':
        row_idx_start = 203
        logs_names = ['TVD', 'GR']
        logs_names_col_idx = [0, 1]
        logs_units = ['ft', 'API']

    else:
        raise ValueError('LAS file location: %s has not been specified.'
                         % las_file_loc)

    attr_mapping_idx, attr_mapping_unit = _get_mapping(logs_names, logs_names_col_idx, logs_units)

    return row_idx_start, attr_mapping_idx, attr_mapping_unit


def get_log_reading_dict(las_file_loc, filternull=True):
    """"
    Return
    - OrderedDict to record each log
    - numeric values of all logs altogether
    """
    row_idx_start, attr_mapping_idx, attr_mapping_unit = get_specific_attr_mapping(las_file_loc)

    # get log numeric values
    # doesn't ignore off values (<0)
    logs_values = []
    with open(las_file_loc) as file:
        for row_idx, row in enumerate(file):
            if row_idx >= row_idx_start:
                row = row.split()
                logs_values.append([float(row[col_idx]) for col_idx in attr_mapping_idx.values()])
    logs_values = np.array(logs_values)

    if filternull:
        # filter non-neg element
        mask = logs_values > 0
        # only rows that contain all pos values are selected
        logs_values = logs_values[mask.all(axis=1)]

    # record each log separately in an ordered dict
    logs_reading_dict = OrderedDict()
    for log_name_idx, log_name in enumerate(attr_mapping_idx.keys()):
        logs_reading_dict[log_name] = logs_values[:, log_name_idx]

    return logs_reading_dict, logs_values


def get_filtered_log_reading_dict(las_file_loc):
    """"Ignore off values in logs_values (only take non-neg)
    Return
    - OrderedDict that filter out non-neg values
     """
    logs_reading_dict, logs_values = get_log_reading_dict(las_file_loc)

    # filter non-neg element
    mask = logs_values > 0
    # only rows that contain all pos values are selected
    logs_values = logs_values[mask.all(axis=1)]

    # # manipulate in pandas
    # logs_values = pd.DataFrame(data=logs_values)
    # # default neg readings to NaN and drop them (in row)
    # logs_values = logs_values.where(logs_values > 0.0).dropna(axis=0)

    for log_name_idx, log_name in enumerate(logs_reading_dict.keys()):
        logs_reading_dict[log_name] = logs_values[:, log_name_idx]

    return logs_reading_dict, logs_values


def merge_logs(all_logs_reading_dicts, all_logs_values, primary_key='TVD'):
    """"Given any logs in dictionary format, find the common rows that contain primary key
    in all logs
    Return:
        - logs_reading_dict: combined log readings per log
        - logs_values: numeric values of the logs
    """

    primary_key_list = []
    non_primary_key_list = []
    for log_reading_idx, log_reading in enumerate(all_logs_reading_dicts):
        # check for primary key
        if primary_key not in log_reading.keys():
            raise ValueError('The primary key %s is missing in log %d.'
                             % (primary_key, log_reading_idx+1))
        else:
            # find index of primary key in each dictionary
            non_primary_key_idxes = []
            for col_idx, col in enumerate(log_reading.keys()):
                if col == primary_key:
                    primary_key_list.append((col, col_idx))
                else:
                    non_primary_key_idxes.append((col, col_idx))
            non_primary_key_list.append(non_primary_key_idxes)

    # recursively find the common depth from all logs_reading_dict based on primary_key
    # append all readings in all logs to a list according to primary key
    log_values_primary_key = [logs_reading_dicts[primary_key]
                              for logs_reading_dicts in all_logs_reading_dicts]

    def _find_common_rows(S):
        # recursive call to find common element
        def _find(S, result, n):
            if n == 0:
                return result
            result = np.intersect1d(S[n-1], result)
            return _find(S, result, n-1)
        return _find(S, result=S[len(S)-1], n=len(S))

    primary_rows = _find_common_rows(log_values_primary_key)

    # filter out rows correspond to primary rows
    for logs_idx, (primary_key, primary_key_idx) in enumerate(primary_key_list):
        mask = np.isin(all_logs_values[logs_idx][:, primary_key_idx], primary_rows)
        all_logs_values[logs_idx] = all_logs_values[logs_idx][mask, :]

    # stack all logs values according to non primary keys
    def _stack_cols(S, non_primary_key_list):
        def _stack(S, non_primary_key_list, start, stop):

            col_name_start = list(zip(*non_primary_key_list[start]))[0]
            col_name_stop = list(zip(*non_primary_key_list[stop]))[0]
            col_idx_start = list(zip(*non_primary_key_list[start]))[1]
            col_idx_stop = list(zip(*non_primary_key_list[stop]))[1]
            if start == stop:
                for log_name, log_idx in zip(col_name_start, col_idx_start):
                    new_dict[log_name] = S[start][:, log_idx]
                new_stack = S[start][:, col_idx_start]
                return new_stack
            elif start == stop - 1:
                for i, _logs_names, _logs_idx in \
                        ((start, col_name_start, col_idx_start), (stop, col_name_stop, col_idx_stop)):
                    for log_name, log_idx in zip(_logs_names, _logs_idx):
                        new_dict[log_name] = S[i][:, log_idx]
                new_stack = np.hstack((S[start][:, col_idx_start], S[stop][:, col_idx_stop]))
                return new_stack
            middle = (start + stop) // 2
            left = _stack(S, non_primary_key_list, start, middle)
            right = _stack(S, non_primary_key_list, middle+1, stop)
            return np.hstack((left, right))
        new_dict = OrderedDict()
        return new_dict, _stack(S, non_primary_key_list, start=0, stop=len(S)-1)

    all_logs_reading_dicts, all_logs_values = _stack_cols(all_logs_values, non_primary_key_list)

    # append primary rows to the new stacked cols and dict
    all_logs_values = np.hstack((all_logs_values, primary_rows.reshape(-1, 1)))
    all_logs_reading_dicts[primary_key] = primary_rows

    return all_logs_reading_dicts, all_logs_values


if __name__ == '__main__':

    las_file_1 = r'../input_template/Middleton Unit B 47-38 No. 8SH__From EDR.las'
    logs_reading_dict1, logs_values1 = get_filtered_log_reading_dict(las_file_1)
    las_file_2 = r'../input_template/LAS Middleton Unit B 47-38 No. 8SH_From MWD.las'
    logs_reading_dict2, logs_values2 = get_filtered_log_reading_dict(las_file_2)
    all_logs_reading_dicts = [logs_reading_dict1, logs_reading_dict2]
    all_logs_values = [logs_values1, logs_values2]


    logs_dict, logs_values = merge_logs(all_logs_reading_dicts, all_logs_values, primary_key='TVD')
    gr = logs_dict['GR']
    wob = logs_dict['WOB']
    area = 6
    rpm = logs_dict['RPM']
    torque = logs_dict['TOR']
    rop = logs_dict['ROP']

    # loc = '../input/input.xlsx'
    # with open(loc) as file:
    #     print('open ok')
    #
    # import pandas as pd
    # data = pd.read_excel(loc)
    # print('pd ok')
