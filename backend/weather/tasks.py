# Task scheduler
from celery import shared_task

# Other libraries
import pytz
from datetime import datetime
import datetime as dt
from meteostat import Hourly

# Importing entry model
from .models import *

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
    latest = Entry.objects.latest('time')
    
    # Setting start and end parameters
    start = latest.time
    end = dt.datetime.now().astimezone(dt.timezone.utc).replace(second=0, microsecond=0)
    
    print(start)
    print(end)
    
    # Get hourly data
    data = Hourly('72219', start, end)
    data = data.fetch()
    
    # Test
    print(data)
    
    if not data.empty:
        # Saving hourly data as entries
        for i in range(len(data)):
            # Access row data using df.iloc[i]
            Entry.add_entry(data.iloc[i])
        # Printing to celery worker debug cmd
        print ("successfully fetched new data")
    else:
        print ("data is up to date")
        
    return