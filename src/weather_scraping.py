import requests
import pandas as pd
from bs4 import BeautifulSoup
from dateutil.parser import parse
from data_prep import add_dash

months = ['januari', 'februari', 'maart', 'april', 'mei', 'juni', 'juli', 'augustus', 'september', 'oktober', 'november', 'december']
years = ['2018', '2019', '2020', '2021']
months_eng = {'januari':'january', 'februari':'february', 'maart':'march', 'april':'april', 
            'mei':'may', 'juni':'june', 'juli':'july', 'augustus':'august', 'september':'september', 'oktober':'october', 
            'november':'november', 'december':'december'}

def get_dates(months: list, years: list):

    dates = []
    for year in years:
        new = add_dash(year, -4)
        for month in months:
            date = month+new
            dates.append(date)
    valid_dates = dates[:43]
    return valid_dates

def scrape_data(dates: list, eng_months: list):
    df_list = []
    for date in dates:
        url = requests.get(f'https://veghelsweer.nl/noaa2/maandoverzicht.php?fichier={date}')
        month = date.split('-')[0]
        year = date.split('-')[1]
        new_month = eng_months[month]
        new_date = f'{new_month}-{year}'
        
        html_text = url.text
        soup = BeautifulSoup(html_text, 'html.parser')
        test = soup.find_all("tr")
        days = test[2:33]

        for i in range(len(days)):
            atts = []
            day = days[i].find_all('td')

            for att in day:
                txt = att.get_text()
                num = txt.split(' ')[0]
                atts.append(num)
            day_date = f'{i+1}-'+new_date
            try:
                datetime = parse(day_date)
            except:
                print(f'date in line {i+1} of month {new_month} does not exist')
            atts.append(datetime)
            df_list.append(atts)
    df = pd.DataFrame(df_list)
    return df

def clean_data(df):
    df = df.dropna()
    df = df.drop([5], axis=1)
    dict_names = {0:'Day', 1: 'Min temp', 2:'Max temp', 3:'Avg temp', 4:'Wind speed', 6:'Precipitation', 7:'Date'}
    df.rename(columns=dict_names, inplace=True)
    df = df[df.Day != 'Totaal']
    df.reset_index(inplace=True)
    df = df.drop('index', axis=1)
    df = df[df.Precipitation != '---']
    df = df.astype({'Min temp': 'float64', 'Max temp': 'float64', 'Avg temp':'float64', 'Wind speed':'float64', 'Precipitation':'float64'})
    return df

def main():
    dates = get_dates(months, years)
    df = scrape_data(dates, months_eng)
    df = clean_data(df)
    df.to_csv('full_weather.csv')

if __name__ == '__main__':
    main()