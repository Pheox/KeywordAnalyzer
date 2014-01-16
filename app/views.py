import csv
import pdb
import json
import urllib, httplib
from datetime import datetime
from StringIO import StringIO
from urlparse import urlparse

from flask import render_template, flash, redirect
from flask import request, Response, jsonify
from flask.ext.babel import gettext
from flask.ext.babel import lazy_gettext
from werkzeug import secure_filename

from app import app, db, babel, dispatcher_thread, analyzer_config
from forms import NewTaskForm, NewURLsTaskForm, SelectKeywordForm, ConfigForm

from models import Task, Filter, Keyword, KeywordPage, TaskPage
from models import Page, Domain, Statistics
from models_dao import TaskDAO, StatisticsDAO, KeywordPageDAO, TaskPageDAO
from models_dao import KeywordDAO, FilterDAO, TaskStateDAO, ConfigurationDAO
from models_dao import PageDAO, DomainDAO

from config import LANGUAGES
from kw_analyzer import KeywordAnalyzer, PageFeatures
from kw_analyzer import LANGS_DICT
from dispatcher import TaskDispatcher



##### Global variables
show_hidden_flag = False


#####

@app.route('/settings', methods=['GET', 'POST'])
def settings():
  """
  Settings page.
  Only one configuration object for now.
  """
  stats = StatisticsDAO.get_stats()
  
  form = ConfigForm()
  if form.validate_on_submit():
    ConfigurationDAO.set_tasks_per_page(form.tasks_per_page.data)
    ConfigurationDAO.set_results_per_page(form.results_per_page.data)

  config = ConfigurationDAO.get_config()
  form = ConfigForm(obj=config)
  form.populate_obj(config)

  return render_template('settings.html',
    is_alive=dispatcher_thread.is_alive(), stats=stats, form=form)


@app.route('/about', methods=['GET'])
def about():
  """
  About page.
  """
  return render_template('about.html', is_alive=dispatcher_thread.is_alive())


@app.route('/show_hidden', methods=['POST'])
def show_hidden():
  """
  Shows hidden tasks.
  """
  global show_hidden_flag

  if request.form['hidden'] == 'Show hidden':
    show_hidden_flag = True
  else:
    show_hidden_flag = False
  return redirect('/')


@app.route('/delete/task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
  TaskDAO.delete_task_shallow(task_id)
  return redirect('/')


@app.route('/export/<task_name>', methods=['POST'])
def export(task_name):
  """ Create a CSV file for a specified task. """
  task = TaskDAO.get_task(int(request.form['to_export']))

  csv_buff = StringIO()
  csv_writer = csv.writer(csv_buff)

  # get all pages with positions
  results = []
  if task.keyword_id:
    results = KeywordPageDAO.get_kw_pages(task)

    csv_writer.writerow(['Engine position', 'URL', 'DA',
        'PA', 'MR', 'PR', 'SR'])
    for kw_page in results:
      row = [kw_page.engine_position,
             kw_page.page.domain.url + kw_page.page.path,
             kw_page.page.domain.da,
             kw_page.page.pa, kw_page.page.mr,
             kw_page.page.pr,
             kw_page.page.sr
      ]
      csv_writer.writerow(row)
  else:
    results = TaskPageDAO.get_task_pages(task)

    csv_writer.writerow(['URL', 'DA', 'PA', 'MR', 'PR', 'SR'])
    for task_page in results:
      row = [task_page.page.domain.url + task_page.page.path,
             task_page.page.domain.da,
             task_page.page.pa, task_page.page.mr,
             task_page.page.pr, task_page.page.sr
             ]
      csv_writer.writerow(row)

  return Response(csv_buff.getvalue(), mimetype="text/csv")


@app.route('/start', methods=['POST'])
def start():
  """ Start a thread that checkes DB for tasks. """
  global dispatcher_thread

  app.logger.info("Starting thread.")
  stats = StatisticsDAO.get_stats()
  try:
    if dispatcher_thread.is_alive():
      app.logger.error("Starting thread, but the thread is already running")
      dispatcher_thread.join()
      dispatcher_thread = TaskDispatcher()
    dispatcher_thread.start()
  except RuntimeError as e:
    app.logger.error("%s\n%s\n%s" % (e,
      traceback.format_exc(),
      sys.exc_info()[0]))
  return redirect('/')


@app.route('/stop', methods=['POST'])
def stop():
  """ Stop the task-processing thread. """
  global dispatcher_thread

  if dispatcher_thread.is_alive():
    app.logger.info("Stoping thread.")
    dispatcher_thread.join()
    dispatcher_thread = TaskDispatcher()
  return redirect('/')


@app.route('/search', methods=['GET', 'POST'])
def search():
  form = SelectKeywordForm()
  kws = KeywordDAO.get_all()

  form.keyword.choices = [(str(kw.id), kw.title) for kw in kws]

  # get keyword ID
  kw_id = 0

  if form.keyword.data != 'None':
    kw_id = int(form.keyword.data)
  else:
    first_kw = KeywordDAO.get_first()
    if first_kw:
      kw_id = first_kw.id

  # get all languages of tasks for specific keyword
  kw_langs = TaskDAO.get_kw_langs(kw_id)

  form.language.choices = [(kw_lang.task.language, LANGS_DICT[kw_lang.task.language]) 
    for kw_lang in kw_langs]

  # get language ID
  lang_id = ''
  if form.language.data != 'None' and form.switch.data == 'lang':
    lang_id = form.language.data
  else:
    if form.language.choices:
      lang_id = form.language.choices[0][0]

  # get all pages of specified language for a specified keyword
  results = PageDAO.get_all_pages(kw_id=kw_id, lang_id=lang_id)

  return render_template('search.html', form=form, results=results,
                         is_alive=dispatcher_thread.is_alive())



@app.route('/show<int:page_tasks>/<int:task_id>/<int:page_results>',
           methods=['GET', 'POST'])
def show_results(page_tasks=1, task_id=None, page_results=0):
  return index(task_id, page_tasks, page_results)


@app.route('/show<int:page_tasks>', methods=['GET', 'POST'])
def show_task(page_tasks=1):
  return index(page_tasks=page_tasks)


@app.route('/', methods=['GET', 'POST'])
def index(task_id=None, page_tasks=1, page_results=0):
  tasks = []
  show_task_results = []
  show_task = None

  config = ConfigurationDAO.get_config()
  tasks = TaskDAO.get_paginated_tasks(page_tasks, config.tasks_per_page, 
    show_hidden_flag)

  if task_id:
    show_task = TaskDAO.get_task(task_id)
    show_task_results = TaskDAO.get_task_results(task_id, page_results, 
      config.results_per_page)

  return render_template('index.html', title='Keyword Analyzer',
    tasks=tasks, is_alive=dispatcher_thread.is_alive(),
    show_hidden=show_hidden_flag, show_task_results=show_task_results,
    show_task=show_task)



@app.route('/new_kw_task', methods=['GET', 'POST'])
def new_kw_task():
  form = NewTaskForm()
  if form.validate_on_submit():
    if add_task(form):
      flash('New Task for keyword "' + form.keyword.data + '"')
      return redirect('/')
    else:
      flash(gettext('Cant add this task!'))

  return render_template('new_kw_task.html', title='Keyword Analyzer',
                         form=form, is_alive=dispatcher_thread.is_alive())


@app.route('/new_urls_task', methods=['GET', 'POST'])
def new_urls_task():
  form = NewURLsTaskForm()
  if form.validate_on_submit():
    if add_urls_task(form):
      flash(form.task_title.data + 'task added.')
    else:
      flash(gettext('Cant add this task!'))

  return render_template('new_urls_task.html', title='Keyword Analyzer',
                         form=form, is_alive=dispatcher_thread.is_alive())


@app.route('/hide_task', methods=['POST'])
def hide_task():
  task = TaskDAO.get_task(int(request.form['to_hide']))

  if request.form['visibility'] == 'Unhide':
    task.hide_flag = False
  else:
    task.hide_flag = True
  db.session.commit()
  return redirect('/')


@app.route('/change_state', methods=['POST'])
def change_state():
  task = TaskDAO.get_task(int(request.form['task_id']))

  if task.state.state_str == 'running':
    dispatcher_thread.stop_task()
    TaskDAO.set_task_state(task, 'stopped')
  elif task.state.state_str == 'stopped':
    TaskDAO.set_task_state(task, 'queued')
  elif task.state.state_str == 'completed':
    TaskDAO.clear_task_shallow(task)
    TaskDAO.set_task_state(task, 'queued')
  elif task.state.state_str == 'queued':
    TaskDAO.set_task_state(task, 'stopped')

  return redirect('/')


def add_urls_task(form):
  reader = csv.reader(form.csv_file.data)
  page_urls = []

  for page_url in reader:
    page_urls.append(page_url)

  task = TaskDAO.add_task(
    title=form.task_title.data, 
    date=datetime.utcnow(),
    max_searches=len(page_urls), 
    state_str='queued', 
    priority=form.priority.data
  )
  
  for page_url in page_urls:
    # need to parse and save both domain and page
    page = PageFeatures()
    page.page = page_url[0]

    domain = DomainDAO.get_or_update_domain(page.domain, page.da) 
    page_db = PageDAO.get_or_update_domain_page(page.domain, page.path, domain)

    TaskPageDAO.add_task_page(task.id, page_db.id)
  return True



def add_task(form):
  # create filter if not exists
  filter = FilterDAO.get_filter(form.da_th.data, form.pa_th.data,
    form.mr_th.data, form.pr_th.data, form.sr_th.data)

  if not filter:
    filter = FilterDAO.add_filter(form.da_th.data, form.pa_th.data,
      form.mr_th.data, form.pr_th.data, form.sr_th.data)
  kw = KeywordDAO.add_if_not_exist(form.keyword.data)

  # create task
  if not Task.query.filter(Task.title==form.task_title.data).count():
    TaskDAO.add_task(
      title=form.task_title.data,
      date=datetime.utcnow(),
      filter_id=filter.id,
      keyword_id=kw.id,
      state_str='queued',
      max_searches=form.max_searches.data,
      language=form.language.data,
      engine=form.engine.data,
      hide_flag=False,
      priority=form.priority.data
    )
    return True
  return False



##### Error handlers
@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


#####  Localization
@babel.localeselector
def get_locale():
  #return 'es'
  return request.accept_languages.best_match(LANGUAGES.keys())
