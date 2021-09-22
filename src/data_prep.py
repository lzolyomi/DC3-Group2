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

def winter_data(path_data: str): # path to the rain historic series folder
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

# def add_dash(string, index):
#     #adds a dash to a string in position index
#     return string[:index] + "-" + string[index:]

# def format_datestring(string):
#     #accepts a datestring from the rain timeseries and formats it
#     date_only = add_dash(string, 8).split("-")[0] #removes the hour
#     date_only = add_dash(date_only, 6) #separate day and month
#     date_only = add_dash(date_only, 4) #separates month and year
#     return date_only

# def return_rain_ts(path_data):
#     """
#     path_data: the path to the data folder (it assumes the structure is unchanged)
#     """
#     files = listdir(path_data)
#     return_dict = {}

#     for filename in files:
#         split = filename.split("_")
#         begin_date = format_datestring(split[3])
#         end_date = format_datestring(split[4].split('.')[0]) #get rid of csv
#         return_dict[begin_date] = filename
    
#     return return_dict
# if platform.system() == 'Windows':  # checks for the system to get the paths right
#     s = '''\\'''
# else:
#     s = '''/'''
