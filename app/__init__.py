from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.babel import Babel
from momentjs import momentjs


app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

# localization
babel = Babel(app)

# proper datetime handling
app.jinja_env.globals['momentjs'] = momentjs


# Keyword Analyzer initialization
from dispatcher import TaskDispatcher
dispatcher_thread = TaskDispatcher()


# logging (add email logging for errors)
import logging
from logging.handlers import RotatingFileHandler, SMTPHandler
from config import ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD

app.logger.removeHandler(app.logger.handlers[0])
app.logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')

file_handler = RotatingFileHandler('app.log', 'a', 1 * 1024 * 1024, 10)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
app.logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.DEBUG)
app.logger.addHandler(console_handler)

credentials = None
if MAIL_USERNAME or MAIL_PASSWORD:
    credentials = (MAIL_USERNAME, MAIL_PASSWORD)
mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT),
                           'no-reply@' + MAIL_SERVER,
                           ADMINS, 'kw_moz failure',
                           credentials)
mail_handler.setLevel(logging.ERROR)
app.logger.addHandler(mail_handler)


from analyzer_config import AnalyzerConfig
# keyword analyzer configuration
analyzer_config = AnalyzerConfig()

from app import views, models
