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

# Django db query
from django.db.models import Q

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
    
    # Calculating accuracy
    accuracy.delay()
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

# Calculating accuracy
@shared_task
def accuracy():
    # Getting predictions that have been predicted over 24 hours ago
    est_elapsed = (dt.datetime.utcnow() - dt.timedelta(hours=entry_cycle)).replace(tzinfo=pytz.utc)
    predictions = Prediction.objects.filter(Q(prediction_time__lte=est_elapsed))

    # Running loop to calculate accuracy of all predictions
    for prediction in tqdm(predictions, desc="Calculating accuracy..."):
        if (prediction.accuracy!=-1):
            # Getting predicted_entries of a prediction
            prediction_id = prediction.id
            predicted_entries = read_frame(Predicted_Entry.objects.filter(prediction_id=prediction_id)).copy(deep=True)
            
            # Getting start and end time of a prediction
            start_time = predicted_entries.iloc[0]['time']
            end_time = predicted_entries.iloc[-1]['time']
            
            # Dropping unecessary columns
            predicted_entries.drop(columns=['id', 'prediction', 'time', 'coco'], inplace=True)
            
            # Getting actual entries
            actual_entries = read_frame(Entry.objects.filter(time__range=(start_time, end_time))).copy(deep=True)
            actual_entries.drop(columns=['id', 'time', 'coco'], inplace=True)
            
            # Calculating residuals
            error = (actual_entries - predicted_entries).div(actual_entries)
        
            # Calculating error
            error_temp = error['temp'].abs().mean()*100
            error_dwpt = error['dwpt'].abs().mean()*100
            error_rhum = error['rhum'].abs().mean()*100
            error_wdir = error['wdir'].abs().mean()*100
            error_wspd = error['wspd'].abs().mean()*100
            error_pres = error['pres'].abs().mean()*100
            
            # Calculating accuracy
            accuracy_temp = 100 - error_temp
            accuracy_dwpt = 100 - error_dwpt
            accuracy_rhum = 100 - error_rhum
            accuracy_wdir = 100 - error_wdir
            accuracy_wspd = 100 - error_wspd
            accuracy_pres = 100 - error_pres
            
            # Calculating general accuracy and saving
            accuracy = (accuracy_temp + accuracy_dwpt + accuracy_rhum + accuracy_wdir + accuracy_wspd + accuracy_pres)/6
            prediction.accuracy_temp = accuracy_temp
            prediction.accuracy_dwpt = accuracy_dwpt
            prediction.accuracy_rhum = accuracy_rhum
            prediction.accuracy_wdir = accuracy_wdir
            prediction.accuracy_wspd = accuracy_wspd
            prediction.accuracy_pres = accuracy_pres
            prediction.accuracy = accuracy
            prediction.save()
    print("Accuracy calculated!")
    return