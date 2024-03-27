# Weather forecasting backend/automated script

Weather forecasting assignment

## Table of Contents

- [About](#about)
- [Installation](#installation)
- [Usage](#usage)

## About

Automated weather forecasting backend using django + celery

## Installation
List step-by-step instructions on how to install the project

Pulling and running development server 
```
env\Scripts\activate
pip install celery celery[rabbitmq] django-celery-results meteostat 
cd backend
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

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