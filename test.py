import pandas as pd

filename = 'FormattedData.csv'

df = pd.read_csv(filename, usecols = ['Received','estimate', 'Time2', 'X0.10sec', 'X11.120sec', 'X2.3min', 'X3.5min', 'Over_5min'])
t = 45
df2 = df.loc[df['Time2'] <= t].iloc[-1]['estimate']
print(df2)

df3 = df['X0.10sec'][0]
print(df3)