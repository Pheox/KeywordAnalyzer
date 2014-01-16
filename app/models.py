from app import db
from datetime import datetime

"""
List of models:
- KeywordPage
- TaskPage
- Page
- Task
- Keyword
- Filter
- Domain
- Statistics
- TaskState
- Configuration
"""



SEARCH_ENGINES = ('google', 'bing', 'yahoo')
SEARCH_LANGUAGES = ('en', 'it', 'de', 'fr', 'nl', 'ru', 'ro', 'es')


class KeywordPage(db.Model):
  __tablename__ = 'keyword_page'
  keyword_id = db.Column(db.Integer, db.ForeignKey('keyword.id'),
                        primary_key=True)
  page_id = db.Column(db.Integer, db.ForeignKey('page.id'),
                      primary_key=True)
  task_id = db.Column(db.Integer, db.ForeignKey('task.id'),
                      primary_key=True)

  page = db.relationship('Page', backref='kw_pages')
  keyword = db.relationship('Keyword', backref='kw_pages')

  engine_position = db.Column(db.Integer, default=0)
  #filter = db.Column(db.Integer, db.ForeignKey('filter.id'))


class TaskPage(db.Model):
  __tablename__ = 'task_page'
  task_id = db.Column(db.Integer, db.ForeignKey('task.id'), primary_key=True)
  page_id = db.Column(db.Integer, db.ForeignKey('page.id'), primary_key=True)
  page = db.relationship('Page', backref='task_pages')
  done_flag = db.Column(db.Boolean, default=False)


class Page(db.Model):
  __tablename__ = 'page'
  id = db.Column(db.Integer, primary_key=True)
  path = db.Column(db.String(100), index=True, nullable=False)
  date = db.Column(db.DateTime, default=datetime(1970, 1, 1))
  domain_id = db.Column(db.Integer, db.ForeignKey('domain.id'))
  pa = db.Column(db.Integer, default=0)
  mr = db.Column(db.Integer, default=0)
  pr = db.Column(db.Integer, default=0)
  sr = db.Column(db.Integer, default=0)

  def __repr__(self):
    return "This is page"


class Task(db.Model):
  __tablename__ = 'task'
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(100), index=True, unique=True)
  keyword_id = db.Column(db.Integer, db.ForeignKey('keyword.id'))
  engine = db.Column(db.String(30), default=SEARCH_ENGINES[0])
  language = db.Column(db.String(10), default=SEARCH_LANGUAGES[0])
  date = db.Column(db.DateTime)
  max_searches = db.Column(db.Integer, default=1000)
  searches_done = db.Column(db.Integer, default=0)
  filter_id = db.Column(db.Integer, db.ForeignKey('filter.id'))
  state_id = db.Column(db.Integer, db.ForeignKey('task_state.id'))
  hide_flag = db.Column(db.Boolean, nullable=False, default=False)
  priority = db.Column(db.Integer, default=0)
  kw_pages = db.relationship('KeywordPage', backref='task',
    primaryjoin='(Task.id==KeywordPage.task_id)', lazy='dynamic')
  pages = db.relationship('TaskPage', backref='task',
    primaryjoin='(Task.id==TaskPage.task_id)', lazy='dynamic')

  def __repr__(self):
    if self.keyword:
      return 'Task %s for keyword %s.' % (self.title, self.keyword.title)
    return 'Task %s without keyword.' % self.title


class Keyword(db.Model):
  __tablename__ = 'keyword'
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(100), index=True, unique=True, nullable=False)
  kw_tasks = db.relationship('Task', backref='keyword',
    primaryjoin="(Keyword.id==Task.keyword_id)", lazy='dynamic')
  #pages = db.relationship('Page', secondary=keyword_pages,
  #  backref=db.backref('kw_pages', lazy='dynamic'))
  #pages = db.relationship('KeywordPage', backref='keyword')

  def __repr__(self):
    return 'Keyword %s' % self.title


class Filter(db.Model):
  __tablename__ = 'filter'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), index=True, unique=True)
  da_th = db.Column(db.Integer, default=0)
  pa_th = db.Column(db.Integer, default=0)
  mr_th = db.Column(db.Integer, default=0)
  pr_th = db.Column(db.Integer, default=0)
  sr_th = db.Column(db.Integer, default=0)
  tasks = db.relationship('Task', backref='filter',
    primaryjoin="(Filter.id==Task.filter_id)", lazy='dynamic')

  def __repr__(self):
    return 'Filter %s: %d %d %d %d %d' % (self.name, self.da_th, self.pa_th,
      self.mr_th, self.pr_th, self.sr_th)


class Domain(db.Model):
  __tablename__ = 'domain'
  id = db.Column(db.Integer, primary_key=True)
  url = db.Column(db.String(150), index=True, unique=True, nullable=False)
  date = db.Column(db.Date, default=datetime(1970, 1, 1))
  da = db.Column(db.Integer, default=0)
  pages = db.relationship('Page', backref='domain',
    primaryjoin="(Domain.id==Page.domain_id)", lazy='dynamic')

  def __repr__(self):
    return 'Domain: %s' % self.url


class Statistics(db.Model):
  __tablename__ = 'statistics'
  id = db.Column(db.Integer, primary_key=True)
  moz_queries = db.Column(db.Integer)
  google_queries = db.Column(db.Integer)
  yahoo_queries = db.Column(db.Integer)

  def __repr__(self):
    return '''Statistics:\n
      \tmoz queries: %d\n
      \tgoogle queries: %d\n
      \tyahoo queries: %d''' % (self.moz_queries, self.google_queries,
    self.yahoo_queries)


class TaskState(db.Model):
  __tablename__ = 'task_state'
  id = db.Column(db.Integer, primary_key=True)
  state_str = db.Column(db.String(100), unique=True)

  tasks = db.relationship('Task', backref='state',
    primaryjoin="(TaskState.id==Task.state_id)", lazy='dynamic')


class Configuration(db.Model):
  __tablename__ = 'configuration'
  id = db.Column(db.Integer, primary_key=True)
  tasks_per_page = db.Column(db.Integer)
  results_per_page = db.Column(db.Integer)
