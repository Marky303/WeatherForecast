# Task scheduler
from celery import shared_task

# Other libraries
from datetime import datetime
from meteostat import Hourly

# Importing entry model
from .models import *

# Define your tasks here
@shared_task
def ping():
    print("Pong! Your async completed!")
    return

@shared_task
def update_entry():
    # Set time period
    start = datetime(2024, 1, 1)
    end = datetime(2024, 12, 31, 23, 59)
    
    # Get hourly data
    data = Hourly('72219', start, end)
    data = data.fetch()
    
    # Saving hourly data as entries
    for i in range(len(data)):
        # Access row data using df.iloc[i]
        Entry.add_entry(data.iloc[i])
        
    return