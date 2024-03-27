# Weather forecasting backend/automated script

Weather forecasting assignment

## Table of Contents

- [About](#about)
- [Installation](#installation)
- [Usage](#usage)
- [Notes](#note)

## About

Automated weather forecasting backend using django + celery

## Installation
List step-by-step instructions on how to install the project

Install and run rabbitmq message broker

Pulling and running development server 
```
env\Scripts\activate
pip install celery celery[rabbitmq] meteostat 
cd backend
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

Create django superuser
```
env\Scripts\activate
cd backend
python manage.py createsuperuser
```

Navigate to localhost:8000 (django admin page)

Running celery worker in new command prompt
```
env\Scripts\activate
cd backend
celery -A backend worker -l info -P solo
```

Running celery beat scheduler in new command prompt
```
env\Scripts\activate
cd backend
celery -A your_project beat --loglevel=info
```


## Usage

## Note
django_celery_beat can be used to track periodic tasks on django admin page


