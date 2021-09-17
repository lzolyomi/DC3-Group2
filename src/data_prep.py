import pandas as pd 
from os import listdir

def add_dash(string, index):
    #adds a dash to a string in position index
    return string[:index] + "-" + string[index:]

def format_datestring(string):
    #accepts a datestring from the rain timeseries and formats it
    date_only = add_dash(string, 8).split("-")[0] #removes the hour
    date_only = add_dash(date_only, 6) #separate day and month
    date_only = add_dash(date_only, 4) #separates month and year
    return date_only

def return_rain_ts(path_data):
    """
    path_data: the path to the data folder (it assumes the structure is unchanged)
    """
    files = listdir(path_data)
    return_dict = {}

    for filename in files:
        split = filename.split("_")
        begin_date = format_datestring(split[3])
        end_date = format_datestring(split[4].split('.')[0]) #get rid of csv
        return_dict[begin_date] = filename
    
    return return_dict
