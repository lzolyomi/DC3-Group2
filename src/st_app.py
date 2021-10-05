# >>> Library imports
from pandas.core.tools.datetimes import to_datetime
import streamlit as st
import pandas as pd
from streamlit import config 
import plotly.express as px
import platform
import numpy as np
import scipy
from scipy import signal
from scipy.signal import argrelextrema
from streamlit_keplergl import keplergl_static
from keplergl import KeplerGl
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.linear_model import LinearRegression


# >>> .py imports
from data_prep import return_rain_ts
from file_struct import locate_data_, map_settings
from waterway import waterway_complete, list_stuwvak
from baseline import get_winter_data


def filter_data(df: pd.DataFrame, weir, window_length: int = 101, 
                polyorder: int = 3, derivative: int = 0, 
                default: bool = False):    
    '''takes a dataframe (from the "waterway_complete" function) with at least a
    "Diff(Verschil)" column and a "Weir compartment" column. It then applies a
    "Savitzky–Golay" filter to the dataframe. It puts the smoothed out data
    in a new column named "filtered diff". Window_length must be uneven. 
    A derivative column of the line can be extracted by setting the derivative to an int above 0
    Set default to True to not have to give input every time.
    This returns the old dataframe + the new column.
    '''
    # if not default:
    #     print(df_leij['Weir compartment'].unique())
    weir = weir
        

    df_oneweir = df.loc[df['Weir compartment'] == weir]
    filtered = scipy.signal.savgol_filter(df_oneweir['Diff(Verschil)'],
                                          window_length = window_length, polyorder = polyorder, 
                                          deriv=0, delta=1.0, axis=- 1, mode='interp', cval=0.0)
    
    filtered_deriv = scipy.signal.savgol_filter(df_oneweir['Diff(Verschil)'],
                                          window_length = window_length, polyorder = polyorder, 
                                          deriv=derivative, delta=1.0, axis=- 1, mode='interp', cval=0.0)
    
#     print(scipy.signal.savgol_coeffs(window_length, polyorder))
    df_oneweir['filtered diff'] = filtered
    
    if derivative != 0:
        df_oneweir['derivative order ' + str(derivative)] = filtered_deriv

    
    
    return df_oneweir

def plot_filtered(df):
    '''Takes input of dataframe from filter_data and plots output'''
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    for c in df.columns:
        if 'Diff' in c:
            fig.add_trace(go.Scatter(x = df['Time'], y = df[c], name = 'initial data'), secondary_y = False)
        elif 'filtered' in c:
            fig.add_trace(go.Scatter(x = df['Time'], y = df[c], name = 'filtered data'), secondary_y = False)
        elif 'derivative' in c:
            fig.add_trace(go.Scatter(x = df['Time'], y = df[c], name = 'derivative'), secondary_y = True)
    fig.update_layout(title = stream + ' Weir compartment '+ df['Weir compartment'].iloc[0], width=1100,height=700)
    st.plotly_chart(fig, use_container_width=True, width=1100,height=700)

#------------------- Variables to be changed BEFORE running the app
data_path = locate_data_() #path to the data folder 

if platform.system() == 'Windows':  # checks for the system to get the paths right
    s = '''\\'''
else:
    s = '''/'''
    

# ------------------ Data preparations
stuw_order = pd.read_csv(data_path +s+ "stuw_order.csv")
streams = stuw_order["WATERLOOP"].unique()
st.set_page_config(layout="wide")
pd.options.mode.chained_assignment = None  # default='warn'


# ---------------- Layout of the app
stream = st.sidebar.selectbox("Select the stream you want to plot", streams) #stores the stream we want to analyze
compartments = pd.read_csv(data_path +s+ "stuw_order.csv")
compartments = compartments[compartments["WATERLOOP"] == stream]["STUWVAK"].unique()
# ----------------- waterway data and plots
try:
    df_waterway = waterway_complete(stream, data_path +s+ "stuw_order.csv", data_path +s+ "feature_tables" +s)
    df_waterway["Diff(Verschil)"] = df_waterway["Diff(Verschil)"].apply(lambda x: 0 if x < 0 else x) #cuts negative values

except(FileNotFoundError):
    st.markdown("# Not all feature tables available for this stream!")

#..... Select function >>>
func = st.radio("Select function", ["Plots", "Mowing Plots", "Kepler Maps", "Model"], ) #add 'Dataframes' to access dataframe review
rain_ts_dict = return_rain_ts(data_path +s+ "rain_historic_timeseries" +s)

if func == "Plots":

    st.markdown(" ## Plotting the discharge amount in m3 through time ")
    comp = st.sidebar.selectbox("Select the weir compartment",compartments)
    fig1 = px.line(df_waterway, x="Time", y="Discharge(Q)", color="Weir compartment")
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown(" ## Plotting the difference between weir waterheight through time ")

    fig2 = px.line(df_waterway, x="Time", y="Diff(Verschil)", color="Weir compartment")
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown(" ## Plotting Q and Verschil")
    df = pd.read_csv(data_path + s + "feature_tables" + s + comp + "_feature_table.csv") #one feature table
    df["TIME"] = pd.to_datetime(df["TIME"])
    df["YEAR"] = df.apply(lambda x: x["TIME"].year, axis=1)
    df["MONTH"] = df.apply(lambda x: x["TIME"].month, axis=1)
    df
    col = st.radio("Select the value for color", ["YEAR", "MONTH"])
    clipneg = st.checkbox("Do you want to clip negative values?")
    if clipneg == True:
        df["VERSCHIL"] = df.apply(lambda x: x["VERSCHIL"] if x["VERSCHIL"] > 0 else 0, axis=1)
        df["Q"] = df.apply(lambda x: x["Q"] if x["Q"] > 0 else 0, axis=1)
    fig = px.scatter(df, x="Q", y="VERSCHIL", color=col)
    st.plotly_chart(fig)



if func == "Dataframes":
    st.write("Stuw order")
    stuw_order #display dataframe

    comp = st.sidebar.selectbox("Select the weir compartment",compartments) #compartment to look at
    st.write("Example of feature table")
    comp_ft = pd.read_csv(data_path +s+ "feature_tables" +s +f"{comp}_feature_table.csv")
    comp_ft #display dataframe
    st.write("RAM Meteor forecast")
    forecast = pd.read_csv(data_path +s+ "RAM_Meteo_forecast_history.csv")
    #rename columns
    forecast.columns = ["DateTime", "Rainfall_mm", "Cloud_coverage", "Temp", "Modeldate"]
    forecast #display dataframe

    begin_dates = list(rain_ts_dict.keys()) #still need to order
    st.markdown("## Rain timeseries")
    rain_begin_date = st.selectbox("Select start date", begin_dates)
    rain_filename = rain_ts_dict[rain_begin_date] #retrieves the filename
    df_rain = pd.read_csv(data_path +s+ "rain_historic_timeseries"+s+ f"{rain_filename}")
    df_rain # display dataframe


if func == "Mowing Plots":
    comp = st.sidebar.selectbox("Select the weir compartment",compartments) #compartment
    plot_filtered(filter_data(df_waterway, comp, 201, 4, 1))
        

if func == "Kepler Maps":
    st.write("Kepler Maps for all the weirs.")
    df_locations = pd.read_csv(data_path +s+ "geo_loc_final.csv")

    config = map_settings()
    map1 = KeplerGl(width = 800, data={"data_1": df_locations}, config = config)
    keplergl_static(map1)


if func == "Model":
    lg_stuwvak = list_stuwvak("Leijgraaf")
    chosen = st.sidebar.selectbox("Select weir compartment:", lg_stuwvak)
    df = get_winter_data(chosen)
    """Using this data for each compartment,
    a Linear Regression model was fitted."""
    df #display created dataframe
    """The daily average tempretature and the precipitation was used as predictor"""
    
    with st.echo(): #Display code in streamlit
        dct_coef = {}
        for comp in lg_stuwvak:
            #Get winter data for all stuwvak
            data = get_winter_data(comp)
            lg = LinearRegression()
            #fit a linear regression
            lg.fit(X=data[["Avg temp", "Precipitation"]], y=data["VERSCHIL"])
            dct_coef[comp] = lg.coef_ #put coefficients in dictionary
        #reformat data    
        df_dct = {"Stuwvak":[], "Coef avg temp":[], "Coef precipitation":[]}
        for key, lst in dct_coef.items():
            #create new, more concise dataframe
            df_dct["Stuwvak"].append(key)
            df_dct["Coef avg temp"].append(lst[0])
            df_dct["Coef precipitation"].append(lst[1])
    """Result of code:"""
    result = pd.DataFrame(df_dct)





