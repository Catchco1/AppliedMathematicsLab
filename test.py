import pandas as pd

filename = 'ReservationLineData.csv'

df = pd.read_csv(filename, usecols = ['Received','estimate'])
for col in df:
    print(col)
