import pandas as pd

filename = 'FormattedData.csv'

df = pd.read_csv(filename, usecols = ['Received','estimate', 'Time2'])
t = 45
df2 = df.loc[df['Time2'] <= t].iloc[-1]['estimate']
print(df2)

df3 = max(df['estimate'])
print(df3)