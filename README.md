# Big data weather forecasting assignment 
Weather forecasting backend/automated script using [Django](https://www.djangoproject.com/) (Python) + [Celery](https://docs.celeryq.dev/en/stable/) ([RabbitMQ](https://www.rabbitmq.com/)) + MySQL + [Google Looker Studio](https://lookerstudio.google.com/overview)

# Table of Contents
Table of contents of this README.md
- [Introduction](#introduction) 
- [Installation](#installation) Guide on backend installation
- [Usage](#usage)
- [Notes](#notes)

# Introduction

#### General data pipe of this project:
- Weather data is acquired hourly from [Meteostat JSON API](https://dev.meteostat.net/api/). Historical data is taken since the start of 2017 (1/1/2017) from Ho Chi Minh city weather station (station code 48900). **Each entry's features include: time measured (time), temperature (temp), dewpoint (dwpt), humidity (rhum), wind direction (rhum), wind speed (wspd), sea-level air pressure (pres) and weather condition code (coco)**. Hourly task scheduling is achived using Django and Celery.
- After being fetched, weather information will be saved to MySQL database using Django database integration functions.
- Data from database is later queried in order to be analysed using [SARIMA model](https://www.statsmodels.org/dev/generated/statsmodels.tsa.statespace.sarimax.SARIMAX.html) (Seasonal Auto Regressive Integrated Moving Average). Weather condition in the next 24 hours will be predicted and saved to database.
- After 24 hours, accuracy of a prediction can be calculated for each feature. General accuracy can be calculated as the mean of all features' accuracy.
- Historical and predicted data is visualized using Google Looker Studio.

# Installation

#### List step-by-step instructions on how to install the project:
- Install and run RabbitMQ broker server.
- Clone the project 
- Install and run MySQL database. Config MySQL connection in [settings.py](https://github.com/Marky303/WeatherForecast/blob/main/backend/backend/settings.py) (**optional**) 
- Enter project's virtual environment, install required libraries, make database migrations and run development server 
```
env\Scripts\activate
pip install celery celery[rabbitmq] meteostat tqdm django django-pandas numpy pandas django-extensions ipython jupyter notebook==6.5.6 statsmodels matplotlib
cd backend
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
- Create django superuser for admin site (nhien/1234)
```
env\Scripts\activate
cd backend
python manage.py csu
```
- Navigate to localhost:8000/admin (django admin page) and login using the created superuser
- Create a new command prompt and run celery worker
```
env\Scripts\activate
cd backend
celery -A backend worker -l info -P solo
```
- Create a new command prompt and run celery beat scheduler
```
env\Scripts\activate
cd backend
celery -A backend beat --loglevel=info
```
- **Optional**: un-comment `update_entry()` in [backend\backend\urls.py](https://github.com/Marky303/WeatherForecast/blob/main/backend/backend/urls.py)
> [!WARNING]
> There might be problems when migrating Django database when you're using Django provied db.sqlite3 file. Should this happen, delete migrations folder in weather and db.sqlite3 file and run the following `python manage.py makemigrations weather` then `python manage.py migrate`

# Usage

# Notes
#### Important notes that might be helpful when using the project
 - **django_celery_beat** can be used to track periodic tasks on django admin page
 
 - Jupyter notebook can be used as an alternative to Django shell by: 
	  - Running this in a separate (virtual environmented) command prompt **`python manage.py shell_plus --notebook`**
	- Then **add this** to your first cell 
```
		import os, django
		os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
		os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
		django.setup()
```