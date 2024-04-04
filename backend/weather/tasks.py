# Task scheduler's decorator
from celery import shared_task

# Other libraries
import pytz
from datetime import datetime
import datetime as dt
from meteostat import Hourly
from tqdm import tqdm
import pandas as pd
import numpy as np
from django_pandas.io import read_frame
from statsmodels.tsa.statespace.sarimax import SARIMAX

# Importing entry model
from .models import *

# Global variables
# Entries' features
dimensions = ['temp', 'dwpt', 'rhum', 'wdir', 'wspd', 'pres']

# ACF/PACF entry lag
entry_cycle = 24 # hours

# SARIMA components deduced from entry lag
non_seasonal_component = (0,1,0)
seasonal_component = (1, 0, 1, 24)

# Define your tasks here
# Task for async testing
@shared_task
def ping():
    print("Pong! Your async completed!")
    return

# Get weather data on startup and after a time period
# TODO: AVOID GETTING PREDICTED DATA
@shared_task
def update_entry():
    # Get latest entry time from database
    latest = Entry.objects.latest('time') if len(Entry.objects.all()) != 0 else datetime(2017, 1 ,1)
    
    # Setting start and end parameters
    start = (latest.time.replace(tzinfo=None) + dt.timedelta(hours=1)) if len(Entry.objects.all()) != 0 else latest     
    end = dt.datetime.now().astimezone(pytz.utc).replace(tzinfo=None)   
    
    # Get hourly data (from a specific weather station: 48900)
    data = Hourly('48900', start, end)
    data = data.fetch()
    
    if not data.empty:
        # Filling nan values using previous values
        columns_to_fill = ['temp', 'dwpt', 'rhum', 'wdir', 'wspd', 'pres']
        data[columns_to_fill] = data[columns_to_fill].fillna(method='ffill')
        
        # Saving hourly data as entries
        for i in tqdm(range(len(data))):
            # Access row data using df.iloc[i]
            Entry.add_entry(data.iloc[i])
        print ("successfully fetched new data")
        arima.delay() 
    else:
        print ("data is up to date")
    return

# Processing weather data 
@shared_task
def arima():
    train_set = (read_frame(Entry.objects.all())[['time','temp','dwpt','rhum','wdir','wspd','pres','coco']]).copy(deep=True)
        
    # Preparing predictions set
    predictions = (read_frame(Entry.objects.all().order_by('-id')[:entry_cycle])[['time','temp','dwpt','rhum','wdir','wspd','pres','coco']]).copy(deep=True)
    predictions = predictions.sort_values(by='time')
    predictions.reset_index(drop=True, inplace=True)
    
    # Converting from decimal to numpy float64
    train_set[dimensions] = train_set[dimensions].astype(np.float64)
    predictions[dimensions] = predictions[dimensions].astype(np.float64)
    
    for index in range(0,len(predictions)):
        predictions.loc[index, 'time'] += dt.timedelta(hours=entry_cycle)
        
    # Conduct SARIMA on every dimension/feature
    for dimension in tqdm(dimensions, desc="Predicting the next day's features..."):
        # Init SARIMAX model
        model = SARIMAX(np.asarray(train_set[dimension]), order=non_seasonal_component, seasonal_order=seasonal_component)
        model_fit = model.fit()

        # Making predictions
        prediction = model_fit.forecast(entry_cycle)
        predictions[dimension] = prediction
        
    # Create + save prediction instance
    current_time = train_set.iloc[-1].time
    new_prediction_ins = Prediction(prediction_time=current_time, predicted_entry_count=entry_cycle)
    new_prediction_ins.save()
    
    # Create + save predicted entries
    for i in tqdm(range(len(predictions)), desc="Saving predicted values..."):
            Predicted_Entry.add_entry(predictions.iloc[i], new_prediction_ins)

# Calculating residuals