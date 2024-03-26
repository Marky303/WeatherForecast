from celery import shared_task

# Define your tasks here
@shared_task
def simple():
    print("Running properly")
    return

from .models import *
@shared_task
def create_new():
    e = Entry.objects.create(name="new thang",value=1)
    e.save()
    return