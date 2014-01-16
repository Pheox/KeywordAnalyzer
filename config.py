#!flask/bin/python
# -*- coding: utf-8 -*-

import os

# Flask-WTF extension
# CSRF - Cross-site Request Forgery
CSRF_ENABLED = True
SECRET_KEY = 'this-is-secret-key'


# Database setup
basedir = os.path.abspath(os.path.dirname(__file__))

if os.environ.get('DATABASE_URL') is None:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')


# available languages
LANGUAGES = {
    'en': 'English',
    'es': 'Español',
    'cs': 'Čeština'
}

# mail server settings
MAIL_SERVER = 'localhost'
MAIL_PORT = 25
MAIL_USERNAME = None
MAIL_PASSWORD = None

# administrator list
ADMINS = ['vladimirbrigant@gmail.com']
