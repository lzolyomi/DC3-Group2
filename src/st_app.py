import streamlit as st
import pandas as pd 
from waterway import waterway_complete
import plotly.express as px
from data_prep import return_rain_ts
from file_struct import locate_data_
import platform
#------------------- Variables to be changed BEFORE running the app
data_path = locate_data_() #path to the data folder

if platform.system() == 'Windows':  # checks for the system to get the paths right
    s = '''\\'''
else:
    s = '''/'''

# ------------------ Data preparations

stuw_order = pd.read_csv(data_path +s+ "stuw_order.csv")
streams = stuw_order["WATERLOOP"].unique()

# ---------------- Layout of the app
stream = st.sidebar.selectbox("Select the stream you want to plot", streams) #stores the stream we want to analyze

# ----------------- waterway data and plots
try:
    df_waterway = waterway_complete(stream, data_path +s+ "stuw_order.csv", data_path +s+ "feature_tables" +s)
    df_waterway["Diff(Verschil)"] = df_waterway["Diff(Verschil)"].apply(lambda x: 0 if x < 0 else x) #cuts negative values
    compartments = df_waterway["Weir compartment"].unique()
except(FileNotFoundError):
    st.markdown("# Not all feature tables available for this stream!")

#..... Select function >>>
func = st.radio("Select function", ["Plots", "Dataframes"], )
rain_ts_dict = return_rain_ts(data_path +s+ "rain_historic_timeseries" +s)

if func == "Plots":

    st.markdown(" ## Plotting the discharge amount in m3 through time ")

    fig1 = px.line(df_waterway, x="Time", y="Discharge(Q)", color="Weir compartment")
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown(" ## Plotting the difference between weir waterheight through time ")

    fig2 = px.line(df_waterway, x="Time", y="Diff(Verschil)", color="Weir compartment")
    st.plotly_chart(fig2, use_container_width=True)

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
