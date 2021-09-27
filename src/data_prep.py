import pandas as pd 
from os import listdir

def return_rain_ts(path_data):
    files = listdir(path_data)
    return_dict = {}
    
    for filename in files:
        df = pd.read_csv(path_data + filename, nrows=3, header=1)
        datetime = df[['Unnamed: 0']].iloc[1]['Unnamed: 0']
        date = datetime.split(' ')[0]
        return_dict[date] = filename
    
    return return_dict

def winter_rain(path_data: str): # path to the rain historic series folder
    files = listdir(path_data)
    return_dict = {}
    winter_months = ['10', '11', '12', '01', '02']
    
    for filename in files:
        df = pd.read_csv(path_data + filename, nrows=3, header=1)
        datetime = df[['Unnamed: 0']].iloc[1]['Unnamed: 0']
        date = datetime.split(' ')[0]
        if date[3:5] in winter_months:
            return_dict[date] = filename
        
    return return_dict

def winter_weather(path_data: str):
    """
    Returns a dataframe with only the winter data"""
    weather_data = pd.read_csv(path_data + "full_weather.csv")
    winter_months = ['10', '11', '12', '01', '02']
    weather_data["month"] = weather_data.apply(lambda x: x["Date"].split("-")[1], axis=1)
    df = weather_data[weather_data["month"].isin(winter_months)]
    #df.drop("month", axis=1, inplace=True)
    return df

def add_dash(string, index):
    #adds a dash to a string in position index
    return string[:index] + "-" + string[index:]


