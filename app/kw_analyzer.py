#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TODO's
------
- analyzer config class
"""

import urllib2
from urlparse import urlparse
from datetime import datetime, timedelta

from sengines.sengines import GoogleSearch
from seomoz.seomoz import Seomoz, SeomozException
from ranks import getPageRank, getSRank

from app import db, app
from models import Domain, Page
from models_dao import StatisticsDAO


LANGS_DICT = {
    'en': 'English',  # EN
    'it': 'Italian',  # IT
    'de': 'German',  # DE
    'fr': 'French',  # FR
    'nl': 'Dutch',  # NL
    'ru': 'Russian',  # RU
    'ro': 'Romanian',  # RO
    'es': 'Spanish',  # ES
    'pt': 'Portuguese'  # PT
}


class PageFilter(object):
    """ Filtering domains """
    def __init__(self, da_th=0, pa_th=0, mr_th=0, pr_th=0, sr_th=0):
        self.da_th = da_th  # domain_authority threshold
        self.pa_th = pa_th  # page_authority threshold
        self.mr_th = mr_th  # moz_rank threshold
        self.pr_th = pr_th  # page_rank threshold
        self.sr_th = sr_th  # s_rank threshold

    def filter(self, page):
        """ Check domain features of specified domain. """
        if page.da < self.da_th:
            return False
        if page.pa < self.pa_th:
            return False
        if page.mr < self.mr_th:
            return False
        if page.pr >= 0 and page.pr < self.pr_th:
            return False
        if page.sr < self.sr_th:
            return False
        return True


class PageFeatures(object):
    """ Class representing page features like DA, PA, MR, PR, S-Rank."""
    def __init__(self):
        self._position = 0
        self._page = ''
        self._path = ''
        self._domain = ''
        self._da = 0  # Domain Authority (pda)
        self._pa = 0  # Page Authority (upa)
        self._mr = 0  # MOZ Rank (umrp, umrr)
        self._sr = 0  # S-Rank
        self._pr = 0  # PageRank

        self._is_actual = False
        self._exists = False
        self._is_filtered = False

    def _set_position(self, pos):
        self._position = pos

    def _get_position(self):
        return self._position

    position = property(fset=_set_position, fget=_get_position)

    def _set_page(self, page):
        self._page = page
        parsed_url = urlparse(page)
        self._domain = parsed_url.netloc
        # TODO: not good !!
        if self._domain:
            self._path = parsed_url.path
            if parsed_url.params:
                self._path += ';%s' % parsed_url.params
            if parsed_url.query:
                self._path += '?%s' % parsed_url.query
        else:
            self._domain = parsed_url.path
            if self._domain.endswith('/'):
                self._domain = self._domain[:-1]
            self._path = '/'

    def _get_page(self):
        return self._page

    page = property(fset=_set_page, fget=_get_page)

    def _set_domain(self, dom):
        self._domain = dom

    def _get_domain(self):
        return self._domain

    domain = property(fset=_set_domain, fget=_get_domain)

    def _set_path(self, p):
        self._path = p

    def _get_path(self):
        return self._path

    path = property(fset=_set_path, fget=_get_path)

    def _set_da(self, da):
        self._da = da

    def _get_da(self):
        return self._da

    da = property(fset=_set_da, fget=_get_da)

    def _set_pa(self, pa):
        self._pa = pa

    def _get_pa(self):
        return self._pa

    pa = property(fset=_set_pa, fget=_get_pa)

    def _set_mr(self, mr):
        self._mr = mr

    def _get_mr(self):
        return self._mr

    mr = property(fset=_set_mr, fget=_get_mr)

    def _set_pr(self, pr):
        self._pr = pr

    def _get_pr(self):
        return self._pr

    pr = property(fset=_set_pr, fget=_get_pr)

    def _set_sr(self, sr):
        self._sr = sr

    def _get_sr(self):
        return self._sr

    sr = property(fset=_set_sr, fget=_get_sr)

    def _set_is_actual(self, flag):
        self._is_actual = flag

    def _get_is_actual(self):
        return self._is_actual

    is_actual = property(fset=_set_is_actual, fget=_get_is_actual)

    def _set_exists(self, e):
        self._exists = e

    def _get_exists(self):
        return self._exists

    exists = property(fset=_set_exists, fget=_get_exists)

    def _set_is_filtered(self, filtered):
        self._is_filtered = filtered

    def _get_is_filtered(self):
        return self._is_filtered

    is_filtered = property(fset=_set_is_filtered, fget=_get_is_filtered)

    def __repr__(self):
        s = 'Position %d - ' % self.position
        s += 'Page %s' % self.page
        s += 'Domain %s' % self.domain
        s += 'Path %s' % self.path
        s += ': DA=%d PA=%d MR=%d PR=%d SR=%d' % (
            self.da, self.pa, self.mr, self.pr, self.sr)
        return s


class URLsAnalyzer(object):
    """ URLs-analyzing class """

    seomoz_access_id = 'member-cb8c6a3545'
    seomoz_secret_id = '08b3fd7453bdf1e7b452ea09b1174ff2'

    def __init__(self):
        # Mozscape
        self._seomoz = Seomoz(
            URLsAnalyzer.seomoz_access_id, URLsAnalyzer.seomoz_secret_id)

    def analyze_url(self, url):
        page = PageFeatures()
        page.page = url

        result = db.session.query(Page).join(Domain).\
            filter(Domain.url == page.domain, Page.path == page.path).first()

        if result:
            page.exists = True
            hours = datetime.utcnow() - result.date

            if hours < timedelta(hours=48):
                # information are actual for 2 days
                page.is_actual = True
                return page

        StatisticsDAO.inc_moz_queries()
        db.session.commit()

        metrics = self._seomoz.urlMetrics(url)

        page.da = metrics['pda']
        page.pa = metrics['upa']
        page.mr = metrics['umrp']  # umrr
        page.pr = getPageRank(url)
        page.sr = getSRank(url)
        return page


class KeywordAnalyzer(object):
    """ Keyword-analyzing class """

    seomoz_access_id = 'member-cb8c6a3545'
    seomoz_secret_id = '08b3fd7453bdf1e7b452ea09b1174ff2'

    def __init__(self, keyword):
        """
        """
        self.keyword = keyword
        self._max_searches = 100
        self._remaining_searches = self._max_searches
        self._filter = None

        # searcher engine
        self._engine_str = 'google'
        self._engine_position = 0
        self._language = 'en'
        self._engine = GoogleSearch(
            self.keyword.encode('utf8'), lang=self._language,
            lang_restrict="lang_"+self._language)
        self._engine.results_per_page = 25

        # Mozscape
        self._seomoz = Seomoz(
            KeywordAnalyzer.seomoz_access_id, KeywordAnalyzer.seomoz_secret_id)

        self.searched_results = []
        self._page_urls = []
        self._finished = False

    def _set_finished(self, fin):
        self._finished = fin

    def _get_finished(self):
        return self._finished

    finished = property(fset=_set_finished, fget=_get_finished)

    def _set_max_searches(self, ms):
        self._max_searches = ms
        self._remaining_searches = self._max_searches

    def _get_max_searches(self):
        return self._max_searches

    max_searches = property(fset=_set_max_searches, fget=_get_max_searches)

    def _set_filter(self, f):
        self._filter = f

    def _get_filter(self):
        return self._filter

    filter = property(fset=_set_filter, fget=_get_filter)

    def _set_engine(self, engine_str):
        self._engine_str = engine_str
        if self._engine_str == 'google':
            self._engine = GoogleSearch(
                self.keyword.encode('utf8'), lang=self._language,
                lang_restrict="lang_"+self._language)
            self._engine.results_per_page = 25
        elif self._engine_str == 'bing':
            pass  # BING
        elif self._engine_str == 'yahoo':
            pass  # YAHOO

    def _get_engine(self):
        return self._engine_str

    engine = property(fset=_set_engine, fget=_get_engine)

    def _set_engine_position(self, position):
        self._engine_position = position
        if self._max_searches >= self._engine_position:
            self._remaining_searches = self._max_searches-self._engine_position

    def _get_engine_position(self):
        return self._engine_position

    engine_position = property(
        fset=_set_engine_position, fget=_get_engine_position)

    def _set_language(self, lang):
        self._language = lang

    def _get_language(self):
        return self._language

    language = property(fset=_set_language, fget=_get_language)

    def _get_page_features(self, url, position):
        df = PageFeatures()
        df.page = url
        df.position = position

        # check time!
        # co je primary key - path + domain_id ?
        # spravit join page a domain a skontrolovat url a path

        # result = db.session.query(Domain).join(Domain.pages).\
        #  filter(Page.path==df.path, Domain.url==df.domain).all()

        result = db.session.query(Page).join(Domain).\
            filter(Domain.url == df.domain, Page.path == df.path).first()

        if result:
            df.exists = True
            hours = (datetime.utcnow() - result.date).seconds/3600
            if hours < 48:  # information are actual for 2 days
                df.is_actual = True
                df.da = result.domain.da
                df.pa = result.pa
                df.mr = result.mr
                df.pr = result.pr
                df.sr = result.sr
                return df

        metrics = self._seomoz.urlMetrics(url)
        StatisticsDAO.inc_moz_queries()
        db.session.commit()

        try:
            df.da = metrics['pda']
            df.pa = metrics['upa']
            df.mr = metrics['umrp']  # umrr
        except KeyError as e:
            raise SeomozException(e)

        df.pr = getPageRank(url)
        try:
            df.sr = getSRank(url)
        except urllib2.HTTPError as e:
            app.logger.error("bad srank")
            app.logger.error("srank url:" + url)

        return df

    def analyze_next_page(self):
        """ Returns PageFeatures. """
        page = None

        # check if search engine results are ready
        self._get_pages_urls()
        if not self._page_urls:
            app.logger.info('No page url!!!')
            return None

        # get first result
        url, position = self._page_urls.pop(0)

        # Mozscape API

        page = self._get_page_features(url, position)

        if self.filter and not self.filter.filter(page):
            app.logger.debug("Page filtered:\n" + str(page))
            page.is_filtered = True

        return page

    def _get_pages_urls(self):
        """
        Get urls list from search results.
        TODO: max_searches
        """
        # If we finished or no need to use searcher engine, return.
        if not self._remaining_searches or self._page_urls:
            return self._page_urls

        # compute page number
        page_number = self._engine_position/self._engine.results_per_page
        self._engine.page = page_number

        searches_diff = self._remaining_searches-self._engine.results_per_page

        if searches_diff > 0:
            self._remaining_searches -= self._engine.results_per_page
            search_results = self._engine.get_results()[
                (self._engine_position % self._engine.results_per_page):]
        else:
            search_results = self._engine.get_results()[
                (self._engine_position % self._engine.results_per_page):]
            search_results = search_results[:self._remaining_searches]
            self._remaining_searches = 0
        StatisticsDAO.inc_google_queries()

        for result in search_results:
            self._engine_position += 1
            if result.url:
                self._page_urls.append((result.url, self._engine_position))
        return self._page_urls

    def __repr__(self):
        return 'Keyword analyzer for keyword "%s"' % self.keyword


# Test main

if __name__ == '__main__':
    f = PageFilter()

    ka = KeywordAnalyzer("shoe")
    ka.max_searches = 100

    for x in xrange(1, 55):
        page_info = ka.analyze_next_page()
        print page_info
