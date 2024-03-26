# Weather forecasting backend/automated script

Weather forecasting assignment

## Table of Contents

- [About](#about)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## About

Provide a more detailed description of the project. Explain its purpose, features, and any other relevant information.

## Installation
List step-by-step instructions on how to install the project

Pulling and running backend development server
```
env\Scripts\activate
pip install celery celcery[rabbitmq] django-celery-results
cd backend 
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

Running celery in a new window (Rabbitmq installed and running)
```
env\Scripts\activate
cd backend
celery -A backend worker -l info -P solo
```
