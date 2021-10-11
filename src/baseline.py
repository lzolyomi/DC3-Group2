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


def winter_dates(start_year=2018):
    """
    From given start_year returns a list of pairs for each winter period, until 2021"""
    winters = [(f"{start_year}-01-01", f"{start_year}-02-28")]
    for year in range(start_year, 2021):
        winters.append((f"{year}-10-31", f"{year+1}-02-28"))
    return winters

def add_winter_periods(figure):
    """
    Adds rectangles to show the winter periods to the passed figure object
    It must be a px.line figure
    """
    winters = winter_dates()
    for pair in winters:
        figure.add_vrect(x0=pair[0], x1=pair[1], fillcolor="red", opacity=0.2, line_width=0, annotation_text="Winter", annotation_position="top left")


######## End of Levi's functions


### DEBUG code 
if __name__ == "__main__":
    
    print(winter_dates())