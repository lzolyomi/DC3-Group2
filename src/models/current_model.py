import numpy as np
import pandas as pd
import lmfit
import datetime
from datetime import date
from sklearn import linear_model
import datetime
import argparse

pd.options.mode.chained_assignment = None  # default='warn'

#---------------Please adjust variables here or in the command line------------------------------------------------------------

if os.path.isfile('../data/full_weather.csv'):
    data_path='../data/feature_tables/'
else:
    data_path='../../data/feature_tables/'
    
weir='211VEL_211N' #(--weir)
risk_date='2019-06-17' # (--risk_date)
prediction=True # True for prediction (--prediction)
last_days=7 # (--last_days) For prediction: Defines how many days the linear model takes into account to predict the next 21 days
avg_temp=22 # (--avg_temp) For prediction: Average Temperature adjusts the prediction +/- 20%
#---------------End of adjust variables-------------------------------------------------------------------------------------------

# From now on PLEASE DO NOT CHANGE------------------------------------------------------------------------------------------------

def get_data(weir,data_path,date_format=False):
    ''' Get the feature data of the individual weir
    Keyword arguments:
    weir -- the weir name as string
    date_format -- date_format boolean 
    data_path -- the local path of the weir feature data csv's
    Returns: data as dataframe'''
    datapath=data_path+weir+'_feature_table.csv'
    data=pd.read_csv(datapath,index_col="TIME",parse_dates=True)
    if date_format:
        data.index=data.index.strftime('%Y-%m-%d')
    return data
    
def get_model(weir:str,year:int,data_path):
    '''Get the model Aa-en-Maas uses to define the backwater caused in winter
    Keyword arguments:
    weir -- the weir name as string
    year -- year as int
    data_path -- the local path of the weir feature data csv's
    Returns: model'''
    weir_data=get_data(weir,data_path,date_format=True)
    selected_data=weir_data[['VERSCHIL', 'Q']]
    # Set values of Verschil lower than 0 to 0 as backwater cannot be negative
    selected_data['VERSCHIL']=negative_backwater_to_zero(selected_data['VERSCHIL'])
    # Set the Q value also to 0 where backwater is now 0
    selected_data.loc[(selected_data.VERSCHIL == 0),'Q']=0
    # Winter season where plants are "not" growing from 1st October to end of February
    winter_data=selected_data.loc[str(year-1)+'-10-01':str(year)+'-02-31']
    # The polynomial function Aa-en-Maas currently uses
    def eqn_poly(x, a, b):
        ''' simple polynomial function'''
        return  a*(x**b)     
    mod = lmfit.Model(eqn_poly)
    lm_result = mod.fit(np.array(winter_data['VERSCHIL']), x=np.array(winter_data['Q']), a=1.0, b=1.0)
    return lm_result
    
def negative_backwater_to_zero(vegetation_data):
    '''Set values lower than 0 to 0 as backwater cannot be negative'''
    return np.clip(vegetation_data, 0, None)
    
def calc_vegetation(weir,weir_data,risk_date,data_path):
    '''Calculate the back water caused by plants of a single data point
    Keyword arguments:
    weir -- the weir name as string
    weir_data -- the feature data of the weir
    risk_date -- the date where the vegetation risk should be evaluated on
    data_path -- the local path of the weir feature data csv's
    Returns: current vegetation '''
    try:
        # Take the necessary features(VERSCHIL and Q) of the data at the given date
        risk_date_data=weir_data[['VERSCHIL', 'Q']].loc[risk_date]
    except:
        print('This date is not in the database')
    risk_date=datetime.datetime.strptime(risk_date, "%Y-%m-%d")
    current_year=risk_date.year
    try:
        #Get the winter baseline model of the current year
        model=get_model(weir,year=current_year,data_path=data_path)
    except:
        print('Error, model cannot be created for year {}'.format(current_year))
        return 0
    # If the date is in the winter period, 
    if ((risk_date.month <= 2) | (risk_date.month >= 10)):
        # the back water is assumed to be 0 as the plants do "not" grow in winter
        current_vegetation = 0
    elif (risk_date_data.empty):
        print("No flow data for "+ weir+ " on date ", risk_date)
        current_vegetation = None
    elif (len(risk_date_data) == 0):
        print("No data for ", weir, " on date ", risk_date)
        current_vegetation = None
    else:
        # Predict the vegetation for every summer data point based on the winter baseline
        winter_pred = model.eval(x=risk_date_data['Q'])
        winter_pred=negative_backwater_to_zero(winter_pred)
        # Calculate the vegetation by plants: Current back water - predicted back water based on winter
        current_vegetation= risk_date_data.loc["VERSCHIL"] - winter_pred
        current_vegetation=negative_backwater_to_zero(current_vegetation)
    return current_vegetation   
    
def calc_vegetation_risk(weir,risk_date, data_path):
    ''' Calculate the vegetation risk between 1 and 4
    Keyword arguments:
    weir -- the weir name as string
    risk_date -- the date where the vegetation risk should be evaluated on
    data_path -- the local path of the weir feature data csv's
    Returns: Risk category, Quantiles of vegetation 25,50,75'''
    weir_data=get_data(weir,date_format=True,data_path=data_path)
    # Calculate the back water by plants on given date
    current_vegetation=calc_vegetation(weir,weir_data,risk_date,data_path)
    risk_date=datetime.datetime.strptime(risk_date, "%Y-%m-%d")
    current_year=risk_date.year
    min_year=current_year - 3
    total_vegetation=[]
    # Get the vegetation for the last three years
    for year in range(min_year,current_year):
        try: 
            # load model of given year
            model_year =get_model(weir, year=year,data_path=data_path)
        except:
            print('Error,year '+str(year)+' model cannot be created')  
            continue
        # Select summer season data from March till end of September
        summer_data = weir_data.loc[str(year)+'-03-01':str(year)+'-09-31']
        # Predict the vegetation for every summer data point based on the winter baseline
        winter_pred = model_year.eval(x=summer_data['Q']) 
        winter_pred=negative_backwater_to_zero(winter_pred)
        # Calculate the vegetation by plants: Current back water - predicted back water based on winter
        vegetation_year=summer_data.loc[:,"VERSCHIL"]-winter_pred
        vegetation_year=negative_backwater_to_zero(vegetation_year)
        total_vegetation.append(vegetation_year)
    total_vegetation = pd.concat(total_vegetation)
    # Get Quantiles of the total vegetation
    vegetation_q25=np.quantile(total_vegetation,0.25)
    vegetation_q50=np.quantile(total_vegetation,0.50)
    vegetation_q75=np.quantile(total_vegetation,0.75)
    # Get Risk category based on quantile segment
    risk_cat=np.where(current_vegetation > vegetation_q75,4,np.where(current_vegetation > vegetation_q50,3,np.where(current_vegetation > vegetation_q25,2,1))).tolist()
    # Return risk category and the quantiles
    print("The risk category for the date: {} is {}. The following quantiles were used for the risk calculation 0.25:{}, 0.5:{}, 0.75:{}".format(risk_date,risk_cat,vegetation_q25, vegetation_q50, vegetation_q75))
    return [risk_cat,vegetation_q25, vegetation_q50, vegetation_q75]
    
def predict_vegetation(weir,last_days,avg_temp,data_path):
    '''Predict the vegetation of the next 21 days based on the last 7 days with linear model
    Keyword arguments:
    weir -- the weir name as string
    last_days -- the number of days the linear model should base the prediction on
    avg_temp -- the average temperature adjusting the predictions by +/- 20%
    data_path -- the local path of the weir feature data csv's
    Returns: Dataframe of the backwater predictions of the next 21 days'''
    data=get_data(weir,data_path,date_format=True)
    data.reset_index(inplace=True)
    # Get the last data points depending on number of last_days
    last_data=data.tail(last_days)
    # Get last day to calculate 
    last_day = datetime.datetime.strptime(last_data.iloc[-1]['TIME'], "%Y-%m-%d")
    # Get dates of the next 21 days
    new_dates=[last_day+datetime.timedelta(days=i) for i in range(1,22)]
    # Calculate back water by vegetation for the last days
    last_data['vegetation']=last_data['TIME'].apply(lambda row:calc_vegetation(weir,get_data(weir,data_path,date_format=True),row,data_path))
    last_data.reset_index(inplace=True)
    # Define linear model
    reg = linear_model.LinearRegression()
    # Take index and the back water by vegetation as training data
    x_train=last_data.index.to_numpy().reshape(-1, 1)
    y_train=last_data['vegetation'].to_numpy().reshape(-1, 1)
    # Fit the linear model on the last days
    reg.fit(x_train,y_train)
    # Get index for the next 21 days
    x_test=[x_train[-1]+i for i in range(1,22)]
    # Predict the vegetation for the next 21 days
    predictions=reg.predict(x_test)
    # Format
    predictions= [item for elem in predictions.tolist() for item in elem]
    # Depending on the temperature add multplication value to adjust values
    try:
        if (avg_temp > 25):
            predictions=[pred*1.2 for pred in predictions]
        elif (avg_temp<20):
            predictions=[pred*0.8 for pred in predictions]
    except:
        print("The Temperature was not available")
    data = {'TIME':  new_dates,'Predicted backwater by vegetation': predictions}
    df = pd.DataFrame (data, columns = ['TIME','Predicted backwater by vegetation'])
    print(df)
    return df
    
def main():
    parser = argparse.ArgumentParser(description='Arguments get parsed via --commands')
    parser.add_argument('--weir', type=str,default=weir)
    parser.add_argument('--risk_date', type=str, default=risk_date)
    parser.add_argument('--data_path', type=str,default=data_path)
    parser.add_argument('--prediction', type=bool,default=prediction)
    parser.add_argument('--last_days', type=int,default=last_days)
    parser.add_argument('--avg_temp', type=int,default=avg_temp)
    args = parser.parse_args()
    if args.prediction:
        predict_vegetation(weir=args.weir,last_days=args.last_days,avg_temp=args.avg_temp,data_path=args.data_path)
    else:
        calc_vegetation_risk(weir=args.weir,risk_date=args.risk_date, data_path=args.data_path)
    
if __name__ == '__main__':
    main()