import pandas as pd
import numpy as np
import scipy
from scipy import signal
from scipy.signal import argrelextrema
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

pd.options.mode.chained_assignment = None  # default='warn'


def filter_data(df: pd.DataFrame, window_length: int = 101,
                polyorder: int = 3, derivative: int = 0,
                default: bool = False):
    """takes a dataframe (from the "waterway_complete" function) with at least a
    "Diff(Verschil)" column and a "Weir compartment" column. It then applies a
    "Savitzky–Golay" filter to the dataframe. It puts the smoothed out data
    in a new column named "filtered diff". Window_length must be uneven.
    A derivative column of the line can be extracted by setting the derivative to an int above 0
    Set default to True to not have to give input every time.
    This returns the old dataframe + the new column.
    """
    if not default:
        print(df_leij['Weir compartment'].unique())
        weir = input('Copy one of the weirs and paste it in input')
        weir = weir.replace("'", "")
    else:
        weir = '211M_211N'

    df_oneweir = df_leij.loc[df['Weir compartment'] == weir]
    filtered = scipy.signal.savgol_filter(df_oneweir['Diff(Verschil)'],
                                          window_length=window_length, polyorder=polyorder,
                                          deriv=0, delta=1.0,
                                          axis=- 1, mode='interp', cval=0.0)

    filtered_deriv = scipy.signal.savgol_filter(df_oneweir['Diff(Verschil)'],
                                                window_length=window_length, polyorder=polyorder,
                                                deriv=derivative, delta=1.0,
                                                axis=- 1, mode='interp', cval=0.0)

    df_oneweir['filtered diff'] = filtered

    if derivative != 0:
        df_oneweir['derivative order ' + str(derivative)] = filtered_deriv

    return df_oneweir


def plot_filtered(df: pd.DataFrame):
    """ Takes the output from 'filter_data' and plots the original data,
    the filtered data and if there is a derivative column it plots it on
    a separate y axis
    """

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    for c in df.columns:
        if 'Diff' in c:
            fig.add_trace(go.Scatter(x=df['Time'], y=df[c],
                                     name='initial data'), secondary_y=False)
        elif 'filtered' in c:
            fig.add_trace(go.Scatter(x=df['Time'], y=df[c],
                                     name='filtered data'), secondary_y=False)
        elif 'derivative' in c:
            fig.add_trace(go.Scatter(x=df['Time'], y=df[c],
                                     name='derivative'), secondary_y=True)
    fig.update_layout(title='Weir ' + df['Weir compartment'].iloc[0])
    fig.show()


def filter_inacc(data, upper_threshold=0.05, set_to=0):
    """function for setting all verschil below 0.05 to 0 (or whatever you input)
    """
    mask = data['Diff(Verschil)'] > upper_threshold
    test = data
    test['Diff(Verschil)'] = data['Diff(Verschil)'].where(mask, set_to)
    return test


def print_risky_slopes(data, weir='211M_211L', date='2021-02-10', path=path):
    """ This function is by no means complete and needs work but I thought I
    would upload it for people to see what were doing.
    For this one to run you need to import current_model.py as well.
    This takes the data and looks when a certain day Verschil+the derivative*21 will reach
    the 75th percentile threshold.
    """
    lst, pred = calc_vegetation_risk(weir, date, path)
    pred.index = pd.to_datetime(pred.index)
    new_df = data.loc[pred.index[0]: pred.index[-1]]
    new_df['Time'] = new_df['Time'].dt.date
    new_df = new_df.set_index('Time', drop=True)

    new_tst['new_verschil'] = new_tst['Diff(Verschil)'] - pred

    th = .75  # this is just for the print atm
    threshold = lst[-1]  # 75th percentile

    count = 0
    tot_count = 0

    for d in new_tst.index:
        tot_count += 1
        if new_tst.loc[d]['new_verschil'] + new_tst.loc[d]['derivative order 1'] * 21 > threshold:
            for n in range(22):
                if new_tst.loc[d]['new_verschil'] + new_tst.loc[d]['derivative order 1'] * n > threshold:
                    print(str(d)[:10], 'will reach', str(int(th * 100)) + '%', 'in', n, 'days')
                    break
            count += 1

    print('\nTotal days:', tot_count)
    print('Days with risky slopes:', count)
