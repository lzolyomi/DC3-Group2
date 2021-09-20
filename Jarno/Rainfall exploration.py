import pandas as pd
import numpy as np
import plotly.graph_objects as go
import glob
import plotly.express as px

path = '/Users/20182463/Desktop/Data challenge 3/data/rain_historic_timeseries' # use your path
all_files = glob.glob(path + "/*.csv")

dflist = [] #list of the dataframes

for filename in all_files[:14]:  #use :14 for the 5 minute interval data, 14: for the 60 minute interval data
    df = pd.read_csv(filename, skiprows = 2)
    dflist.append(df)

df_rain_full = pd.concat(dflist, axis=0)
df_rain_full = df_rain_full.reset_index()

def get_date(date:str):
    '''
    Cool function that returns the part of the data depending on the year/month/day or hour
    '''
    df_year = []
    list_year = []
    for n in range(len(df_rain_full)):
        if date in df_rain_full['Begin'].iloc[n]:
            list_year.append(list(df_rain_full.iloc[n]))
    df_year = pd.DataFrame(list_year, columns = list(df_rain_full.columns))
    df_year = df_year.drop(columns = 'index')
    return df_year

df_2018 = get_date('2018')

#plots the data of De Hoeven in Haarsteeg
fig = px.line(df_2018,x='Begin', y='De Hoeven(Haarsteeg)')
fig.update_layout(title = 'Rain over time in 2018')
fig.show()