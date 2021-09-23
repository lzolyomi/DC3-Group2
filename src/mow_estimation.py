import pandas as pd
import scipy
from scipy import signal

pd.options.mode.chained_assignment = None  # default='warn'


def filter_data(df: pd.DataFrame, window_length: int = 101, polyorder: int = 3):
    '''takes a dataframe (from the "waterway_complete" function) with at least a
    "Diff(Verschil)" column and a "Weir compartment" column. It then applies a
    "Savitzky–Golay" filter to the dataframe. It puts the smoothed out data
    in a new column named "filtered diff". Window_length must be uneven.
    This returns the old dataframe + the new column.
    '''

    print(df_leij['Weir compartment'].unique())
    weir = input('Copy one of the weirs and paste it in input')
    weir = weir.replace("'", "")

    df_oneweir = df_leij.loc[df['Weir compartment'] == weir]
    filtered = scipy.signal.savgol_filter(df_oneweir['Diff(Verschil)'],
                                          window_length=window_length, polyorder=polyorder,
                                          deriv=0, delta=1.0, axis=- 1, mode='interp', cval=0.0)
    df_oneweir['filtered diff'] = filtered

    return df_oneweir