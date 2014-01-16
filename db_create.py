#!flask/bin/python

from migrate.versioning import api
from config import SQLALCHEMY_DATABASE_URI
from config import SQLALCHEMY_MIGRATE_REPO
from app import db
import os.path

db.create_all()
if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
    api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
else:
    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, api.version(SQLALCHEMY_MIGRATE_REPO))

# initialize database
from app.models_dao import TaskStateDAO, StatisticsDAO, ConfigurationDAO

# add possible task states
TASK_STATES = ('queued', 'running', 'stopped', 'completed')
TaskStateDAO.add_states(TASK_STATES)

# initialize statistics row
StatisticsDAO.add_stats()
ConfigurationDAO.add_config()
