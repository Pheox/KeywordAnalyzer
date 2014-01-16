from datetime import datetime

from app import db, app
from models import Task, TaskPage, Page, Domain, Filter, TaskState
from models import Keyword, KeywordPage, TaskPage
from models import Statistics, Configuration


class PageDAO(object):

  @staticmethod
  def get_page_url(page_id):
    page = Page.query.get(page_id)
    domain = Domain.query.get(page.domain_id)
    return (domain.url + page.path)

  @staticmethod
  def set_page_actual(page_id):
    page = Page.query.get(page_id)
    page.date = datetime.utcnow()
    db.session.commit()

  @staticmethod
  def set_params(page_id, pa, mr, pr, sr):
    page = Page.query.get(page_id)
    page.pa = pa
    page.mr = mr
    page.pr = pr
    page.sr = sr
    db.session.commit()

  @staticmethod
  def set_page_domain_da(page_id, da):
    page = Page.query.get(page_id)
    domain = Domain.query.get(page.domain_id)
    domain.da = da
    db.session.commit()

  @staticmethod
  def get_all_pages(kw_id=None, lang_id=None):
    results = db.session.query(Keyword, KeywordPage, Page, Domain).\
      filter(Keyword.id==kw_id).\
      join(KeywordPage).join(Task).\
      filter(Task.language==lang_id).\
      join(Page).join(Domain).\
      order_by(KeywordPage.engine_position).all()
    return results

  @staticmethod
  def get_or_update_domain_page(page_domain_url, page_path, domain):
    page_db = db.session.query(Page).join(Domain).\
      filter(Domain.url==page_domain_url, Page.path==page_path)
    
    if page_db.count():
      page_db = page_db.first()
    else:
      page_db = Page(path=page_path, domain=domain)
      db.session.add(page_db)
    db.session.commit()

    return page_db





##########

class TaskDAO(object):

  @staticmethod
  def get_task(task_id):
    return Task.query.get(task_id)

  @staticmethod
  def set_task_state(task, state_str):
    state = TaskState.query.filter(TaskState.state_str==state_str).first()
    task.state = state
    db.session.commit()

  @staticmethod
  def change_states(old_state_str, new_state_str):
    old_state = TaskState.query.filter(TaskState.state_str==old_state_str).\
      first()
    new_state = TaskState.query.filter(TaskState.state_str==new_state_str).\
      first()

    tasks = Task.query.filter(Task.state_id==old_state.id).all()
    for task in tasks:
        task.state = new_state
    db.session.commit()

  @staticmethod
  def get_task_to_process():
    state = TaskState.query.filter(TaskState.state_str=='queued').first()

    task = Task.query.filter(Task.state_id==state.id, Task.hide_flag==False).\
      order_by(Task.priority.desc(), Task.date).first()
    return task

  @staticmethod
  def get_undone_task_pages(task):
    task_pages = TaskPage.query.filter(TaskPage.task_id==task.id,
        TaskPage.done_flag==False)
    return task_pages

  @staticmethod
  def set_done_task_page(task_page):
    task_page.done_flag = True
    db.session.commit()

  @staticmethod
  def clear_task_shallow(task):
    if not task.keyword_id:
      # if keyword is not set, delete only task and TaskPage-s
      task_pages = TaskPage.query.filter(TaskPage.task_id==task.id).all()
      for task_page in task_pages:
        task_page.done_flag = False
      db.session.commit()
    else:
      # KeywordPage-s and Task
      keyword_pages = KeywordPage.query.\
        filter(KeywordPage.task_id==task.id).all()
      for keyword_page in keyword_pages:
        db.session.delete(keyword_page)
      db.session.commit()

    task.searches_done = 0
    task.date = datetime.utcnow()
    task.hide_flag = False
    db.session.commit()

  @staticmethod
  def delete_task_shallow(task_id):
    task = Task.query.get(task_id)
    TaskDAO.clear_task_shallow(task)

    # if no KeywordPages exists for specified Keyword,
    # delete Keyword from database
    if task.keyword_id:
      keyword_pages = KeywordPage.query.\
        filter(KeywordPage.keyword_id==task.keyword_id).first()
      if not keyword_pages:
        kw = Keyword.query.get(task.keyword_id)
        db.session.delete(kw)
    else:
      task_pages = TaskPage.query.filter(TaskPage.task_id==task.id).all()
      for task_page in task_pages:
        db.session.delete(task_page)
      db.session.commit()

    db.session.delete(task)
    db.session.commit()


  @staticmethod
  def get_kw_results(task_id):
    show_task = Task.query.get(task_id)
    results = db.session.query(Keyword, KeywordPage, Page, Domain).\
      filter(Keyword.id==show_task.keyword_id).\
      join(KeywordPage).join(Page).join(Domain).\
      order_by(KeywordPage.engine_position).all()
    return results


  @staticmethod
  def get_urls_results(task_id):
    show_task = Task.query.get(task_id)
    tasks = db.session.query(TaskPage, Page, Domain).\
      filter(TaskPage.task_id==show_task.id).join(Page).\
      join(Domain).all()
    return tasks

  @staticmethod
  def get_kw_langs(kw_id):
    langs = db.session.query(KeywordPage).\
      filter(KeywordPage.keyword_id==kw_id).join(Task).\
      group_by(Task.language).all()
    return langs

  @staticmethod
  def get_paginated_tasks(page_tasks, tasks_per_page, hidden_flag=False):
    tasks = []
    if hidden_flag:
      tasks = Task.query.order_by(Task.priority.desc(), Task.date).\
        paginate(page_tasks, tasks_per_page, False)
    else:
      tasks = Task.query.filter(Task.hide_flag==False).\
        order_by(Task.priority.desc(), Task.date).\
        paginate(page_tasks, tasks_per_page, False)
    return tasks

  @staticmethod
  def get_task_results(task_id, page_results, results_per_page):
    show_task = TaskDAO.get_task(task_id)
    show_task_results = []

    if show_task.keyword_id:
      show_task_results = KeywordPage.query.\
        filter(KeywordPage.keyword_id==show_task.keyword_id).\
        filter(KeywordPage.task_id==show_task.id).\
        join(Keyword).join(Page).join(Domain).\
        order_by(KeywordPage.engine_position).\
        paginate(page_results, results_per_page, False)
    else:
      show_task_results = TaskPage.query.\
        filter(TaskPage.task_id==show_task.id).join(Page).join(Domain).\
        paginate(page_results, results_per_page, False)
    return show_task_results


  @staticmethod
  def add_task(title, date, state_str, priority=None, filter_id=None, 
    keyword_id=None, max_searches=None, language=None, engine=None, 
    hide_flag=None):
  
    state = TaskStateDAO.get_state(state_str)
    task = Task(title=title, date=date, state=state, priority=priority)
    if filter_id:
      task.filter_id = filter_id
    if keyword_id:
      task.keyword_id = keyword_id
    if max_searches:
      task.max_searches = max_searches
    if language:
      task.language = language
    if engine:
      task.engine = engine
    if hide_flag:
      task.hide_flag = hide_flag
    
    db.session.add(task)
    db.session.commit()
    return task




##########

class StatisticsDAO(object):

  @staticmethod
  def add_stats():
    stats = Statistics(moz_queries=0, google_queries=0, yahoo_queries=0)
    db.session.add(stats)
    db.session.commit()

  @staticmethod
  def get_stats():
    return Statistics.query.first()

  @staticmethod
  def inc_google_queries():
    stats = Statistics.query.first()
    stats.google_queries += 1
    db.session.commit()

  @staticmethod
  def inc_yahoo_queries():
    stats = Statistics.query.first()
    stats.yahoo_queries += 1
    db.session.commit()

  @staticmethod
  def inc_moz_queries():
    stats = Statistics.query.first()
    stats.moz_queries += 1
    db.session.commit()


##########

class KeywordPageDAO(object):

  @staticmethod
  def get_kw_pages(task):
    return KeywordPage.query.\
      filter(KeywordPage.keyword_id==task.keyword_id).\
      filter(KeywordPage.task_id==task.id).\
        join(Keyword).join(Page).join(Domain).\
        order_by(KeywordPage.engine_position).all()

  @staticmethod
  def add_kw_page(task, page):
    page_db = db.session.query(Page).join(Domain).\
        filter(Domain.url==page.domain, Page.path==page.path).first()

    # check if KeywordPage exists
    kw_page = db.session.query(KeywordPage).\
      filter(KeywordPage.keyword_id==task.keyword_id).\
      filter(KeywordPage.page_id==page_db.id).\
      filter(KeywordPage.task_id==task.id).first()

    if kw_page:
      kw_page.engine_position = page.position
    else:
      kw_page = KeywordPage(keyword_id=task.keyword_id, page_id=page_db.id,
        task_id=task.id, engine_position=page.position)
      db.session.add(kw_page)
    db.session.commit()
    return kw_page

##########

class TaskPageDAO(object):

  @staticmethod
  def get_task_pages(task):
    return TaskPage.query.\
      filter(TaskPage.task_id==task.id).\
      filter(TaskPage.done_flag==True).\
      join(Page).join(Domain).all()

  @staticmethod
  def add_task_page(task_id, page_id):
    task_page = TaskPage(task_id=task_id, page_id=page_id)
    db.session.add(task_page)
    db.session.commit()

##########

class KeywordDAO(object):

  @staticmethod
  def get_all():
    return Keyword.query.all()

  @staticmethod
  def get_first():
    return Keyword.query.first()

  @staticmethod
  def add_if_not_exist(kw_title):
    kw = Keyword.query.filter(Keyword.title==kw_title).first()
    if not kw:
      kw = Keyword(title=kw_title)
      db.session.add(kw)
      db.session.commit()
    return kw


##########

class FilterDAO(object):

  @staticmethod
  def get_filter(da_th, pa_th, mr_th, pr_th, sr_th):
    return Filter.query.filter(Filter.da_th==da_th,
      Filter.pa_th==pa_th, Filter.mr_th==mr_th,
      Filter.pr_th==pr_th, Filter.sr_th==sr_th).first()

  @staticmethod
  def add_filter(da_th, pa_th, mr_th, pr_th, sr_th):
    filter = Filter(da_th=da_th, pa_th=pa_th, mr_th=mr_th,
      pr_th=pr_th, sr_th=sr_th)
    db.session.add(filter)
    db.session.commit()
    return filter

##########

class TaskStateDAO(object):

  @staticmethod
  def add_state(state_str):
    state = TaskState(state_str=state_str)
    db.session.add(state)
    db.session.commit()

  @staticmethod
  def add_states(states):
    for state in states:
      TaskStateDAO.add_state(state)

  @staticmethod
  def get_state(state_str):
    return TaskState.query.filter(TaskState.state_str==state_str).first()

##########

class DomainDAO(object):

  @staticmethod
  def get_domain_by_url(url):
    domain = db.session.query(Domain).filter(Domain.url==url)
    return domain

  @staticmethod
  def get_or_update_domain(page_domain_url, page_da):
    domain = DomainDAO.get_domain_by_url(page_domain_url)
    if domain.count():
      domain = domain.first()
    else:
      domain = Domain(url=page_domain_url, da=page_da)
      db.session.add(domain)
    db.session.commit()
    return domain






##########

class ConfigurationDAO(object):

  @staticmethod
  def set_tasks_per_page(num):
    config = Configuration.query.first()
    config.tasks_per_page = num
    db.session.commit()

  @staticmethod
  def set_results_per_page(num):
    config = Configuration.query.first()
    config.results_per_page = num
    db.session.commit()

  @staticmethod
  def get_config():
    return Configuration.query.first()

  @staticmethod
  def add_config():
    config = Configuration(tasks_per_page=5, results_per_page=10)
    db.session.add(config)
    db.session.commit()

