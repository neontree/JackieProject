import numpy as np
import pandas as pd


def input_output_split(df, input_names, output_names, to_numpy=True):
    """Expecting input_names and output_names to filter out in and out"""
    df_in = df.loc[:, input_names]
    df_out = df.loc[:, output_names]

    if to_numpy:
        return df_in.values, df_out.values
    else:
        return df_in, df_out


def input_output_concatenate(data_in, data_out):
    return np.concatenate((data_in, data_out), axis=1)


def timeseries_generator(data_in, data_out, min_index=0, max_index=None, lookback=2, delay=0,
                         include_out=True,
                         shuffle=False, batch_size=32, step=1):
    """Adopted and modified from Deep Learning by Francois Chollet, listing 6.33, page 211
    """

    # concatenate output as one of the input from previous timesteps
    if include_out:
        data_in = input_output_concatenate(data_in, data_out)

    if max_index is None:
        max_index = len(data_in) - delay - 1
    i = min_index + lookback

    while True:
        if shuffle:
            rows = np.random.randint(
                min_index + lookback, max_index, size=batch_size
            )
        else:
            if i + batch_size >= max_index:     # if already beyond limit
                i = min_index + lookback        # reset pointer i
            rows = np.arange(i, min(i + batch_size, max_index))
            i += len(rows)                      # within batch_sizes and not exceeding max

        # holder type for dataframe
        samples = np.zeros((len(rows), lookback//step, data_in.shape[-1]))
        targets = np.zeros((len(rows), data_out.shape[-1]))

        for j, row in enumerate(rows):
            indices = range(rows[j] - lookback, rows[j], step)
            samples[j] = data_in[indices]
            targets[j] = data_out[rows[j] + delay]

        yield samples, targets


if __name__ == '__main__':
    from machine_learning.configurationGR import input_output_dict
    import pandas as pd

    input_name = input_output_dict['INPUT']
    output_name = input_output_dict['OUTPUT']

    file_loc = '../../input/cleaned_up/25509696_cleaned_up.csv'
    df = pd.read_csv(file_loc)

    data_in, data_out = input_output_split(df, input_name, output_name)
    # print(df_in.head(), df_out.head())

    dataset = input_output_concatenate(data_in, data_out)

    # generage a couple of timeseries sample test
    i = 0
    for _ in timeseries_generator(data_in, data_out, min_index=0, max_index=20,
                                  batch_size=10):
        i += 1
        print(_)
        if i == 4:
            break