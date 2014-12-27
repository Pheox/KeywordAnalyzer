import sys
import time
import threading
from datetime import datetime
import traceback

from models import Page, Domain
from models_dao import TaskDAO, PageDAO, KeywordPageDAO
from kw_analyzer import KeywordAnalyzer, PageFilter, URLsAnalyzer
from app import db, app
from seomoz.seomoz import SeomozException


class TaskDispatcher(threading.Thread):

    def __init__(self):
        super(TaskDispatcher, self).__init__()
        self.kill_request = threading.Event()
        self.stop_request = threading.Event()
        self.analyzer = None
        self.task = None

    def stop_task(self):
        if self.task:
            self.stop_request.set()

    def join(self, timeout=None):
        self.kill_request.set()
        super(TaskDispatcher, self).join(timeout)

    def _init_kw_analyzer(self, task):
        self.task = task
        self.analyzer = KeywordAnalyzer(task.keyword.title)
        self.analyzer.language = task.language  # language has to be set first
        self.analyzer.engine = task.engine
        self.analyzer.max_searches = task.max_searches
        self.analyzer.engine_position = task.searches_done

        filter = PageFilter(task.filter.da_th, task.filter.pa_th,
                            task.filter.mr_th, task.filter.pr_th,
                            task.filter.sr_th)
        self.analyzer.filter = filter

    def _init_urls_analyzer(self, task):
        self.task = task
        self.analyzer = URLsAnalyzer()

    def _save_page(self, page):

        # save or update domain
        domain = db.session.query(Domain).filter(Domain.url == page.domain)
        if domain.count():
            if not page.is_actual:
                domain.update({'da': page.da, 'date': datetime.utcnow()})
            domain = domain.first()
        else:
            domain = Domain(url=page.domain, da=page.da,
                            date=datetime.utcnow())
            db.session.add(domain)
        db.session.commit()

        # save or update page
        page_db = db.session.query(Page).join(Domain).\
            filter(Domain.url == page.domain, Page.path == page.path)

        if page_db.count():
            if not page.is_actual:
                page_db.update({'date': datetime.utcnow(), 'pa': page.pa,
                                'mr': page.mr, 'pr': page.pr, 'sr': page.sr})
            page_db = page_db.first()
        else:
            page_db = Page(path=page.path, date=datetime.utcnow(),
                           domain=domain, pa=page.pa, mr=page.mr,
                           pr=page.pr, sr=page.sr)
            db.session.add(page_db)
        db.session.commit()

    def _run_urls_analyzer(self, task):
        self._init_urls_analyzer(task)

        # get all undone TaskPages for a given task
        task_pages = TaskDAO.get_undone_task_pages(task)

        for task_page in task_pages:
            if self.stop_request.isSet():
                TaskDAO.set_task_state(task, 'stopped')
                self.stop_request = threading.Event()
                return

            if self.kill_request.isSet():
                return

            page_url = PageDAO.get_page_url(task_page.page_id)

            try:
                page = self.analyzer.analyze_url(page_url)
            except SeomozException as e:
                task.searches_done += 1
                db.session.commit()
                app.logger.error("SeomozException\n%s\n%s\n%s\n" %
                                 (e, traceback.format_exc(),
                                  sys.exc_info()[0]))
                continue

            TaskDAO.set_done_task_page(task_page)
            if not page.is_actual:
                PageDAO.set_page_actual(task_page.page_id)
                PageDAO.set_params(task_page.page_id, pa=page.pa,
                                   mr=page.mr, pr=page.pr, sr=page.sr)
                PageDAO.set_page_domain_da(task_page.page_id, page.da)

            task.searches_done += 1
            db.session.commit()
        TaskDAO.set_task_state(task, 'completed')

    def _run_kw_analyzer(self, task):
        self._init_kw_analyzer(task)

        for i in range(self.analyzer.max_searches - task.searches_done):
            if self.stop_request.isSet():
                TaskDAO.set_task_state(task, 'stopped')
                self.stop_request = threading.Event()
                return

            if self.kill_request.isSet():
                return

            try:
                page = self.analyzer.analyze_next_page()
            except SeomozException as e:
                task.searches_done += 1
                db.session.commit()
                app.logger.error("SeomozException\n%s\n%s\n%s\n" % (e,
                                 traceback.format_exc(), sys.exc_info()[0]))
                continue

            if not page:
                app.logger.info("Breaking")
                break

            task.searches_done += 1
            db.session.commit()

            self._save_page(page)
            if not page.is_filtered:
                KeywordPageDAO.add_kw_page(task, page)

        task.max_searches = task.searches_done
        db.session.commit()
        TaskDAO.set_task_state(task, 'completed')

    def _process_task(self, task):
        TaskDAO.set_task_state(task, 'running')
        app.logger.info('Dispatching task: %s' % task)

        if not task.keyword_id:
            self._run_urls_analyzer(task)
        else:
            self._run_kw_analyzer(task)

    def _ensure_no_running(self):
        TaskDAO.change_states('running', 'queued')

    def run(self):
        """ Running task-processing loop. """
        self._ensure_no_running()
        task = None
        counter = 0

        while not self.kill_request.isSet():
            task = TaskDAO.get_task_to_process()

            if not task:
                self._ensure_no_running()
                if counter % 100 == 0:
                    app.logger.debug('No task to process!')
                counter += 1
                time.sleep(3)
            else:
                try:
                    self._process_task(task)
                except Exception as e:
                    TaskDAO.set_task_state(task, 'stopped')
                    app.logger.error("Unknown exception\n%s\n%s\n%s\n" % (e,
                                     traceback.format_exc(),
                                     sys.exc_info()[0]))

        if task:
            TaskDAO.set_task_state(task, 'queued')
