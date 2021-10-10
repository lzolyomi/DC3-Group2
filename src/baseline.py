from os import read
import pandas as pd

from data_prep import winter_weather
from file_struct import correct_slash, locate_data_
from waterway import list_stuwvak

d = locate_data_()
s = correct_slash()

######## All of these functions written by Levi, if in doubt, contact me

def get_winter_data(stuwvak: str):
    """ Returns df with weather and feature table data
    for specified stuwvak"""   
    weather = winter_weather(d + s)
    weather["TIME"] = pd.to_datetime(weather["Date"])
    weather.drop(columns=["month", "Date"], inplace = True)
    df = pd.read_csv(d + s + "feature_tables" + s + stuwvak + "_feature_table.csv")
    df["TIME"] = pd.to_datetime(pd.to_datetime(df["TIME"]).dt.date) #need to fix this mf somehow ~Levi
    ready_data = pd.merge(weather, df, on="TIME")
    ready_data.drop(columns=["Unnamed: 0", "Day", "STUWVAK"], inplace=True)
    #delete row if no negative clip needed
    ready_data["VERSCHIL"] = ready_data.apply(lambda x: 0 if x["VERSCHIL"] < 0 else x["VERSCHIL"], axis=1)
    #ready_data['Q'] = ready_data.apply(lambda x: 0 if )

    return ready_data




######## End of Levi's functions