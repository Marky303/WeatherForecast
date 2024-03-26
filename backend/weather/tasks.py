from celery import shared_task

# Simple task
import time

@shared_task
def simple():
    print("Running properly")
    return