# SEEM REDUNDANT AT THE MOMENT
from collections import defaultdict


def read_config(file_path):
    input_output_dict = defaultdict()
    with open(file_path) as file:
        for row in file:

            # check input/output indicator
            if row == 'INPUT':
                key = 'INPUT'
                continue
            elif row == 'OUTPUT':
                key = 'OUTPUT'
                continue

            # append to dictionary list
            input_output_dict[key].append(row)

    return input_output_dict

