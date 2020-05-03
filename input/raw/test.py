import pandas as pd

file = 'La Muela Quick PSA 3H_Bit 8 75_Mud 13 4.csv'
df = pd.read_csv(file)
org_df = df
df = df.dropna()._get_numeric_data().values
condition = df > 0
df = org_df[condition]

print(df.head())