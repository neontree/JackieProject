import pandas as pd


def read(input_loc):
    """Return input from input template
    Input:
        input_df: follow format from input_template/input_template.xlsx
    Output:
        Bit area: in
        Mud weight: ppm
        Logs values: """

    # bit area
    df = pd.read_excel(input_loc, sheet_name='drilling bit')
    bit_area = df.loc[1, 'Bit area']

    # drilling mud
    df = pd.read_excel(input_loc, sheet_name='drilling mud')
    mud_weight = df.loc[1, 'Mud weight']

    # logs values
    df = pd.read_excel(input_loc, sheet_name='logs')
    logs_values = df.iloc[1:, 1:]

    return bit_area, mud_weight, logs_values


if __name__ == '__main__':
    import pandas as pd
    input_loc = r'../input/input.xlsx'

    bit_area, mud_weight, logs_values = read(input_loc)
    print(logs_values)

