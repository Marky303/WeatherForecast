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
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
import category_encoders as ce
import gc

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
parameter_dict = {'temp': [(2,1,2),(2,0,3,8), 'c', 'lbfgs'], 
                  'dwpt': [([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],0,2),(0,0,2,24), 'ct', 'cg'], 
                  'rhum': [(22,1,0),(0,0,6,8), 'c', 'cg'], 
                  'wspd': [([1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],0,2),(0,0,2,24), 'c', 'cg'], 
                  'wdir': [(2,0,2),(2, 0, [0, 1, 0, 1], 12), 'c', 'cg'], 
                  'pres': [(2,0,2),(4,0,4,12), 'c', 'cg']}

# Dictionary reduced to 5 categories
# 0 means fair
# 1 means cloudy/foggy
# 2 means rain
# 3 means shower
# 4 means stormy
mapping_dict = {1: 0, 
                2: 0, 
                3: 1, 
                4: 1, 
                5: 1,
                7: 2,
                8: 2,
                9: 2,
                17: 3,
                18: 3,
                25: 4,
                26: 4,
                27: 4,}

# Dictionary reduced to predicting rain or not
rain_or_not = {1: 0, 
                2: 0, 
                3: 0, 
                4: 0, 
                5: 0,
                7: 1,
                8: 1,
                9: 1,
                17: 1,
                18: 1,
                25: 1,
                26: 1,
                27: 1,}

# Define your tasks here
# Task for async testing
@shared_task
def ping():
    print("Pong! Your async completed!")
    return

# Get weather data on startup and after a time period
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
    
    # Specific customizations (1)
    train_set['pres'] = train_set['pres'] - 1000
    
    for index in range(0,len(predictions)):
        predictions.loc[index, 'time'] += dt.timedelta(hours=entry_cycle)
        
    # Conduct SARIMA on every dimension/feature
    for dimension in tqdm(dimensions, desc="Predicting the next day's features..."):
        # Init SARIMAX model
        model = SARIMAX(np.asarray(train_set[dimension]), order=parameter_dict[dimension][0], seasonal_order=parameter_dict[dimension][1], trend=parameter_dict[dimension][2])
        model_fit = model.fit(method=parameter_dict[dimension][3])

        # Making predictions
        prediction = model_fit.forecast(entry_cycle)
        predictions[dimension] = prediction
        
        # Deallocate memory
        del model
        del model_fit
        gc.collect()

    # Specific customizations (2)
    predictions['pres'] = predictions['pres'] + 1000
        
    # Create + save prediction instance
    current_time = train_set.iloc[-1].time
    new_prediction_ins = Prediction(prediction_time=current_time, predicted_entry_count=entry_cycle)
    
    # Predict weather condition
    predictions = coco(predictions)
    predictions = rain(predictions)
    
    # Create + save predicted entries
    new_prediction_ins.save()
    for i in tqdm(range(len(predictions)), desc="Saving predicted values..."):
            Predicted_Entry.add_entry(predictions.iloc[i], new_prediction_ins)

@shared_task
def coco(predictions):
    # Preparing training set
    # Chooose a start date
    start_date = dt.datetime(2020, 1, 1).replace(tzinfo=pytz.UTC)

    # Getting data from database
    data = (read_frame(Entry.objects.filter(Q(time__gte=start_date)))).copy(deep=True)
    data[dimensions] = data[dimensions].astype(np.float64)

    # Filter nan (0) values
    data = data[data['coco'] != 0]

    # Map available conditions
    data['coco'] = data['coco'].map(mapping_dict)

    # Convert to int and -1 
    data['coco'] = data['coco'].astype(int)    

    # Splitting point/label set
    data_point_set = data.drop(columns=['coco', 'time', 'id'])
    # Encode train label into binary
    binary_encoder = ce.BinaryEncoder(cols=['coco'])
    data_label_set = binary_encoder.fit_transform(data[['coco']])

    # Create polynomial features of degree 6
    poly_features = PolynomialFeatures(degree=6)
    poly = poly_features.fit_transform(data_point_set)

    # Fit linear regression model on le polynomial features
    model = LinearRegression()
    model.fit(poly, data_label_set)

    # Making predictions
    X_plot_poly = poly_features.transform(predictions[dimensions])
    y_pred = model.predict(X_plot_poly)

    # Convert to dataframe
    y_pred = np.clip(y_pred, 0, 1)
    y_pred = y_pred.round()
    y_pred = y_pred.astype(int)

    # Inverse transform
    column_names = ['coco_0', 'coco_1', 'coco_2']
    y_pred = pd.DataFrame(y_pred, columns=column_names)
    y_pred_trans = pd.DataFrame(columns=['coco'])
    for i in range(0,len(y_pred)):
        try:
            y_pred_trans.loc[i] = [binary_encoder.inverse_transform(pd.DataFrame(y_pred.iloc[i]).T).iloc[0].coco]
        except Exception as e:
            y_pred_trans.loc[i] = [-1]

    # Align with the db norm
    y_pred_trans += 1

    # Change prediction's column
    predictions['coco'] = y_pred_trans['coco']

    print("Predicted condition code")

    return predictions

# Predict risk of raining
@shared_task
def rain(predictions):
    # Preparing training set
    # Chooose a start date
    start_date = dt.datetime(2020, 1, 1).replace(tzinfo=pytz.UTC)

    # Getting data from database
    data = (read_frame(Entry.objects.filter(Q(time__gte=start_date)))).copy(deep=True)
    data[dimensions] = data[dimensions].astype(np.float64)

    # Filter nan (0) values
    data = data[data['coco'] != 0]

    # Map available conditions
    data['coco'] = data['coco'].map(rain_or_not)

    # Convert to int and -1 
    data['coco'] = data['coco'].astype(int)    

    # Splitting point/label set
    data_point_set = data.drop(columns=['coco', 'time', 'id'])
    # Encode train label into binary
    data_label_set = data['coco']

    # Create polynomial features of degree 6
    poly_features = PolynomialFeatures(degree=4)
    poly = poly_features.fit_transform(data_point_set)

    # Fit linear regression model on le polynomial features
    model = LinearRegression()
    model.fit(poly, data_label_set)

    # Making predictions
    X_plot_poly = poly_features.transform(predictions[dimensions])
    y_pred = model.predict(X_plot_poly)

    # Convert to dataframe
    y_pred = np.clip(y_pred, 0, 1)
    
    # Change prediction's column
    predictions['risk'] = y_pred

    print("Predicted risk of rain")

    return predictions

# Calculating accuracy
@shared_task
def accuracy():
    # Getting predictions that have been predicted over 24 hours ago
    est_elapsed = (dt.datetime.utcnow() - dt.timedelta(hours=entry_cycle)).replace(tzinfo=pytz.utc)
    predictions = Prediction.objects.filter(Q(prediction_time__lte=est_elapsed))

    # Running loop to calculate accuracy of all predictions
    for prediction in tqdm(predictions, desc="Calculating accuracy..."):
        if (prediction.accuracy==-1):
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