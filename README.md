# RunningCause
A django project to provide runners an easy to use interface to gather money
from sponsors when running for a good cause.

## Development environment

Setting up a development environment on a Ubuntu machine, you'll have to do the
following.

### Python 2.7 and virtualenv

Make sure you have both python 2.7 and the virtualenv tool installed.  

### Install the postgresql dependency

	sudo apt-get install libpq-dev

### Install the Python dependencies

	pip install -r requirements.txt

## Developing on 

Make sure you have the postgresql headers installed

		brew install postgresql

Create a virtual environment and activate it

		virtualenv -p python2.7 .venv
 		source venv/bin/activate

Install all the dependencies

		pip install -r requirements.txt

Create a local settings file

		touch RunningCause/settings/local.py

Add the following content and adjust it to your needs

```python
from .base import *

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
SECRET_KEY = 'very-secure'
DEBUG = True
ALLOWED_HOSTS = ['*', ]
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

```

Run the database migrations

		./manage.py migrate

Create yourself a super user

		./manage.py createsuperuser

Build the static assets

		npm install

Start up the development server

		./manage.py runserver

Update translations

		./manage.py makemessages

## Production requirements (on heroku)

 * redis
 * celery
 * postgresql

### celery

	celery -A RunningCause worker --loglevel=debug

### Deployment
A webhook is placed on GitHub that asks Heroku to deploy the site whenever
changes are pushed to the ´development´ branch.
