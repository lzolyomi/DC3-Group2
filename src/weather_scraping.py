from bs4 import BeautifulSoup
import requests
import numpy as np
import pandas as pd 

# Change the url here 
url = "https://veghelsweer.nl/noaa2/maandoverzicht.php?fichier=juli-2021"



def get_website(url):
    """
    Returns table object from url to a beautifulsoup set object"""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    rows = soup.find("table")
    data_rows = rows.find_all("tr")[2:] #rows from table
    return data_rows

def get_weather_df(data_rows):
    """
    Creates a dataframe from a bs4 set object"""
    indices = [1,2,3,4,5,7]
    data_dct = {"Day":[], "Temp-min":[], "Temp-max":[], "Temp-avg":[], "Wind":[], "Rain":[]}
    for row in data_rows: 
        formatted = np.array(row.text.split("\n"))
        if len(formatted) > 1:
            datapoints = list(formatted[indices])
            for pt, key in zip(datapoints,  data_dct.keys()):
                data_dct[key].append(pt)
    return pd.DataFrame(data_dct) 

def get_weather(url):
    bs_set = get_website(url)
    df = get_weather_df(bs_set)
    return df

