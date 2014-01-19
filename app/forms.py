from flask.ext.wtf import HiddenField, Form, Required
from wtforms import TextField, BooleanField, SelectField, FileField
from wtforms.validators import Required

from kw_analyzer import LANGS_DICT


class SelectKeywordForm(Form):
  """ Form for selecting a keyword. """
  switch = HiddenField("switch")
  keyword = SelectField('keyword', validators=[Required()], choices=[])
  language = SelectField('language', validators=[Required()], choices=[])
  search_engine = SelectField('search_engine',
    choices=[('in_progress', 'in_progress')]) # remove


class NewURLsTaskForm(Form):
  """ Form for a new URLs task. """
  task_title = TextField('task_title', validators=[Required()])
  priority = SelectField('priority', choices=[
    ('0', '0 (lowest)'),
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5 (highest)')
  ])
  csv_file = FileField("Import URLs", validators=[Required()])


class NewTaskForm(Form):
  """ Form for a new task. """
  task_title = TextField('task_title', validators=[Required()])
  keyword = TextField('keyword', validators=[Required()])
  engine = SelectField('search_engine', choices=[
    ('google', 'Google'),
    ('yahoo', 'Yahoo')
  ])
  language = SelectField('language', choices=
    [(abbrev, lang) for (abbrev, lang) in LANGS_DICT.iteritems()])
  max_searches = TextField('max_searches', validators=[Required()])
  da_th = TextField('da_th', validators=[Required()], default=0)
  pa_th = TextField('pa_th', validators=[Required()], default=0)
  mr_th = TextField('mr_th', validators=[Required()], default=0)
  pr_th = TextField('pr_th', validators=[Required()], default=0)
  sr_th = TextField('sr_th', validators=[Required()], default=0)
  priority = SelectField('priority', choices=[
    ('0', '0 (lowest)'),
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5 (highest)')
  ])


class ConfigForm(Form):
  """ Configuration form. """
  # seomoz_access_id
  # seomoz_secret_key
  tasks_per_page = SelectField('tasks_per_page', choices=[
    ('5', '5'),
    ('10', '10'),
    ('25', '25'),
    ('50', '50'),
    ('100', '100')
  ])
  results_per_page = SelectField('results_per_page', choices=[
    ('5', '5'),
    ('10', '10'),
    ('25', '25'),
    ('50', '50'),
    ('100', '100')
  ])

