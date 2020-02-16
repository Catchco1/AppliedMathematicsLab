import pandas as pd

filename = 'FormattedData.csv'

df = pd.read_csv(filename, usecols = ['Received','estimate', 'Time2'])
t = 0
df2 = df.loc[df['Time2'] <= t].iloc[-1]['Received'] / 15
print(df2)
