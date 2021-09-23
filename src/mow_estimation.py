import pandas as pd
import numpy as np
import scipy
from scipy import signal
from scipy.signal import argrelextrema
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

pd.options.mode.chained_assignment = None  # default='warn'


def filter_data(df: pd.DataFrame, window_length: int = 101, polyorder: int = 3):
    """takes a dataframe (from the "waterway_complete" function) with at least a
    "Diff(Verschil)" column and a "Weir compartment" column. It then applies a
    "Savitzky–Golay" filter to the dataframe. It puts the smoothed out data
    in a new column named "filtered diff". Window_length must be uneven.
    This returns the old dataframe + the new column.
    """

    print(df_leij['Weir compartment'].unique())
    weir = input('Copy one of the weirs and paste it in input')
    weir = weir.replace("'", "")

    df_oneweir = df_leij.loc[df['Weir compartment'] == weir]
    filtered = scipy.signal.savgol_filter(df_oneweir['Diff(Verschil)'],
                                          window_length=window_length, polyorder=polyorder,
                                          deriv=0, delta=1.0, axis=- 1, mode='interp', cval=0.0)
    df_oneweir['filtered diff'] = filtered

    return df_oneweir


def plot_filtered(df: pd.DataFrame):
    """ Takes the output from 'filter_data' and plots the original data,
    the filtered data and if there is a derivative column it plots it on
    a separate y axis"""

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
