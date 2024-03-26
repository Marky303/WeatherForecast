from celery import shared_task

import time

while True:
    print("Running properly")
    time.sleep(3)
