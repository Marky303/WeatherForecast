# Task scheduler's decorator
from celery import shared_task

# Other libraries
import pytz
from datetime import datetime
import datetime as dt
from meteostat import Hourly
from tqdm import tqdm
import pandas as pd
from django_pandas.io import read_frame

# Importing entry model
from .models import *

# Global variables
dimensions = ['temp', 'dwpt', 'rhum', 'wdir', 'wspd', 'pres']

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
    else:
        print ("data is up to date")
    return

# Processing weather data 
@shared_task
def arima():
    # Getting training set
    training_set = read_frame(Entry.objects.all())
    
    # Preparing predictions set
    predictions = read_frame(Entry.objects.all().order_by('-id')[:24]).sort_values(by='time')
    for index in range(0,len(predictions)):
        print(index)
        predictions.iloc[index].time = predictions.iloc[index].time + dt.timedelta(days=1)
        # predictions.loc[index, 'time'] = predictions.iloc[index].time + dt.timedelta(days=1)
    predictions = predictions.drop(columns=['id'])
    
    
    
    print("Train")
    print(training_set[len(training_set)-24:])
    print("Not Train")
    print(predictions)
        
        
    
    
    