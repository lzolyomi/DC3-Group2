# >>> Library imports
from numpy import core
from pandas.core.tools.datetimes import to_datetime
import streamlit as st
import pandas as pd
from streamlit import config 
import plotly.express as px
import plotly.graph_objects as go
import platform
import numpy as np
import scipy
from scipy import signal
from scipy.signal import argrelextrema

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.linear_model import LinearRegression


# >>> .py imports
from data_prep import prep_single_df, return_rain_ts
from file_struct import locate_data_, map_settings
from waterway import waterway_complete, list_stuwvak, get_summary_stats
from baseline import get_winter_data, add_winter_periods, create_corr_barchart

######################################################################################################
#                               Functions
######################################################################################################


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


######################################################################################################
#                               Start of dashboard
######################################################################################################
st.set_page_config(layout="wide")

if float(st.__version__.replace('.', '', 1)) <= 11:
    # only streamlit 1.0.0 supports columns
    # this avoids compatibility issues
    cols = True
else:
    cols = False
    from streamlit_keplergl import keplergl_static
    from keplergl import KeplerGl
#------------------- Variables to be changed BEFORE running the app
data_path = locate_data_() #path to the data folder 

if platform.system() == 'Windows':  # checks for the system to get the paths right
    s = '''\\'''
else:
    s = '''/'''
    

# ------------------ Data preparations
stuw_order = pd.read_csv(data_path +s+ "stuw_order.csv")
streams = stuw_order["WATERLOOP"].unique()
pd.options.mode.chained_assignment = None  # default='warn'


# ---------------- Layout of the app
func = st.sidebar.radio("Select function", ["Plots", "Mowing Plots", "Kepler Maps", "Model"], ) #add 'Dataframes' to access dataframe review
stream = st.sidebar.selectbox("Select the stream you want to plot", streams) #stores the stream we want to analyze
compartments = pd.read_csv(data_path +s+ "stuw_order.csv")
compartments = compartments[compartments["WATERLOOP"] == stream]["STUWVAK"].unique()

# ----------------- waterway data and plots
try:
    df_waterway = waterway_complete(stream, data_path +s+ "stuw_order.csv", data_path +s+ "feature_tables" +s)
    df_waterway["Diff(Verschil)"] = df_waterway["Diff(Verschil)"].apply(lambda x: 0 if x < 0 else x) #cuts negative values
except(FileNotFoundError):
    st.warning("# Not all feature tables available for this stream!")

#..... Select function >>>

rain_ts_dict = return_rain_ts(data_path +s+ "rain_historic_timeseries" +s)

######################################################################################################
#                               Start of tab Plots
######################################################################################################

if func == "Plots":
    st.markdown(" ## Plotting the discharge amount in m3 through time ")
    only_one = st.checkbox("Only plot selected compartment", value=True)
    comp = st.sidebar.selectbox("Select the weir compartment",compartments)
    df = pd.read_csv(data_path + s + "feature_tables" + s + comp + "_feature_table.csv") #one feature table
    if only_one:
        fig1 = px.line(df, x="TIME", y="Q")
        fig2 = px.line(df, x="TIME", y="VERSCHIL")
        fig2.add_hline(y=0.05, line_dash='dash', line_color="orange", annotation_text="Accuracy boundary", annotation_position="top left")
        add_winter_periods(fig2)
        add_winter_periods(fig1)
    else:
        fig1 = px.line(df_waterway, x="Time", y="Discharge(Q)", color="Weir compartment")
        fig2 = px.line(df_waterway, x="Time", y="Diff(Verschil)", color="Weir compartment")
        add_winter_periods(fig2)
        add_winter_periods(fig1)
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown(" ## Plotting the difference between weir waterheight through time ")
    st.plotly_chart(fig2, use_container_width=True)

    ############################################################
        #Start of scatter plots and other assisting features


    st.markdown(" ## Plotting Q and Verschil")
    
    df = prep_single_df(comp)
    # add yearly options for slider
    years = [2018, 2019, 2020, 2021]


    if cols:
        col1, col2, col3 = st.columns(3)
        col = col1.radio("Select value for color", ["MONTH", "WINTER"], help="Choose WINTER if you want to see data colored according to which winter season it belongs to")
        clipneg = col2.checkbox("Do you want to clip negative values?")
        only_winter = col2.checkbox("Only show winter data points")
    else:
        col = st.radio("Select the value for color", ["MONTH", "WINTER"], help="Choose WINTER if you want to see data colored according to which winter season it belongs to")
        clipneg = st.checkbox("Do you want to clip negative values?")
        only_winter = st.checkbox("Only show winter data points")

    
    if clipneg == True:
        df["VERSCHIL"] = df.apply(lambda x: x["VERSCHIL"] if x["VERSCHIL"] > 0 else 0, axis=1)
        df["Q"] = df.apply(lambda x: x["Q"] if x["Q"] > 0 else 0, axis=1)
    if only_winter:
        winter_months = [10, 11, 12, 1, 2]
        df = df[df["MONTH"].isin(winter_months)]

    year = st.select_slider("Choose a single year to show:", options=years)
    # Make the dataframe with sliders option data
    new_df = df[df['YEAR']==year]
    fig = px.scatter(new_df, title="Scatterplot with Q and Verschil", x="Q", y="VERSCHIL", color=col, width=600)


    df_barchart = create_corr_barchart(df)
    fig4 = go.Figure(data=[
    go.Bar(name="corr", x=df_barchart.year, y=df_barchart.correlation,text="correlation", textposition="auto", textangle=40),
    go.Bar(name="inaccuracy", x=df_barchart.year, y=df_barchart.ratio_innacurate, text="% inaccurate", textposition="auto", textangle=40)
    ])

    fig4.update_layout(barmode="group", showlegend=False)
    

    if cols:
        col1, col2 = st.columns(2)
        col1.plotly_chart(fig)
        col2.plotly_chart(fig4)
    else:
        st.plotly_chart(fig)
        st.plotly_chart(fig4)


    #### code for summary stats violin plot replaced to baseline_note.ipynb if needed
    

    correlation = round(np.corrcoef(df["Q"], df["VERSCHIL"])[0,1], 2)
    if correlation < -0.5:
        st.markdown(f"Correlation between Q and Verschil: {correlation}")
    elif correlation > 0.5:
        st.markdown(f"Correlation between Q and Verschil: {correlation}")
    else:
        st.markdown(f"Correlation of {correlation} is not sufficient")

######################################################################################################
#                               Start of tab dataframes(not in use)
######################################################################################################


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

######################################################################################################
#                               Start of tab Mowing plots
######################################################################################################


if func == "Mowing Plots":
    comp = st.sidebar.selectbox("Select the weir compartment",compartments) #compartment
    wind_len = st.sidebar.number_input("Filter Window Length (Days)", min_value = 3, step = 2, value = 201)
    polorder = st.sidebar.number_input("Smoothing Approximation Order", min_value= 1, step=1, value = 5)
    wind = wind_len
    if wind % 2 == 0:
        wind -= 1
        #wind_len = st.sidebar.number_input("Filter Window Length (Days)", min_value = 3, step = 2, value = wind)
    plot_filtered(filter_data(df = df_waterway, weir = comp, window_length=wind, polyorder=polorder,  derivative = 1))
        

######################################################################################################
#                               Start of tab kepler maps
######################################################################################################


if func == "Kepler Maps":
    st.write("Kepler Maps for all the weirs.")
    df_locations = pd.read_csv(data_path +s+ "geo_loc_final.csv")

    config = map_settings()
    map1 = KeplerGl(width = 800, data={"data_1": df_locations}, config = config)
    keplergl_static(map1)

######################################################################################################
#                               Start of tab Model (old)
######################################################################################################


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





