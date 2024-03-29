#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
TODO's:
1. check xgoogle library - and results parsing
2. create API
3. analyze antibot system
4.Beautiful license - ok?

API:
gs = GoogleSearch("keyword")
gs.results_per_page = 100
gs.get_results()
gs.get_urls()

"""

import re
import urllib
from abc import abstractmethod
from htmlentitydefs import name2codepoint
from BeautifulSoup import BeautifulSoup
from browser import Browser, BrowserError

#import sys
#sys.path.append("..")



class SearchError(Exception):
    """
    Base class for Google Search exceptions.
    """
    pass



class SearchEngineException(Exception):
  """ An error messages wrapper. """
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return str(self.value)
  def __repr__(self):
    return repr(self.value)





class SearchResult:
  """ Search result wrapper: title, url, desc - nothing more ??"""
  def __init__(self, title, url, desc):
    self.title = title
    self.url = url
    self.desc = desc

  def __repr__(self):
    return 'Google Search Result: "%s"' % self.title.encode('utf-8')


class SearchEngine(object):
  """ Abstract class for all search engines. """

  def __init__(self):
    pass

  @abstractmethod
  def test(self):
    while False:
      yield None



class ParseError(SearchError):
    """
    Parse error in Google results.
    self.msg attribute contains explanation why parsing failed
    self.tag attribute contains BeautifulSoup object with the most relevant tag that failed to parse
    Thrown only in debug mode
    """

    def __init__(self, msg, tag):
        self.msg = msg
        self.tag = tag

    def __str__(self):
        return self.msg

    def html(self):
        return self.tag.prettify()



class GoogleSearch(SearchEngine):
  """ """
  # 1. page
  SEARCH_URL_0 = "http://www.google.%(tld)s/search?hl=%(lang)s&lr=%(lang_restrict)s&q=%(query)s&btnG=Google+Search"
  NEXT_PAGE_0 = "http://www.google.%(tld)s/search?hl=%(lang)s&lr=%(lang_restrict)s&q=%(query)s&start=%(start)d"
  # num. page
  SEARCH_URL_1 = "http://www.google.%(tld)s/search?hl=%(lang)s&lr=%(lang_restrict)s&q=%(query)s&num=%(num)d&btnG=Google+Search"
  NEXT_PAGE_1 = "http://www.google.%(tld)s/search?hl=%(lang)s&lr=%(lang_restrict)s&q=%(query)s&num=%(num)d&start=%(start)d"

  def __init__(self, query, random_agent=False, debug=False, lang="en", tld="com", lang_restrict="", re_search_strings=None):
      self.query = query
      self.debug = debug
      self.browser = Browser(debug=debug)
      self.results_info = None
      self.eor = False # end of results
      self._page = 0
      self._first_indexed_in_previous = None
      self._filetype = None
      self._last_search_url = None
      self._results_per_page = 50
      self._last_from = 0
      self._lang = lang
      self._tld = tld
      self._lang_restrict = lang_restrict;

      if re_search_strings:
          self._re_search_strings = re_search_strings
      elif lang == "de":
          self._re_search_strings = ("Ergebnisse", "von", u"ungefähr")
      elif lang == "es":
          self._re_search_strings = ("Resultados", "de", "aproximadamente")
      # add more localised versions here
      else:
          self._re_search_strings = ("Results", "of", "about")

      if random_agent:
          self.browser.set_random_user_agent()

  @property
  def num_results(self):
      if not self.results_info:
          page = self._get_results_page()
          self.results_info = self._extract_info(page)

          if self.results_info['total'] == 0:
              self.eor = True
      return self.results_info['total']

  @property
  def last_search_url(self):
      return self._last_search_url

  def _get_page(self):
      return self._page

  def _set_page(self, page):
      self._page = page

  page = property(_get_page, _set_page)

  def _get_first_indexed_in_previous(self):
      return self._first_indexed_in_previous

  def _set_first_indexed_in_previous(self, interval):
      if interval == "day":
          self._first_indexed_in_previous = 'd'
      elif interval == "week":
          self._first_indexed_in_previous = 'w'
      elif interval == "month":
          self._first_indexed_in_previous = 'm'
      elif interval == "year":
          self._first_indexed_in_previous = 'y'
      else:
          # a floating point value is a number of months
          try:
              num = float(interval)
          except ValueError:
              raise SearchError, "Wrong parameter to first_indexed_in_previous: %s" % (str(interval))
          self._first_indexed_in_previous = 'm' + str(interval)

  first_indexed_in_previous = property(_get_first_indexed_in_previous, _set_first_indexed_in_previous, doc="possible values: day, week, month, year, or a float value of months")

  def _get_filetype(self):
      return self._filetype

  def _set_filetype(self, filetype):
      self._filetype = filetype

  filetype = property(_get_filetype, _set_filetype, doc="file extension to search for")

  def _get_results_per_page(self):
    return self._results_per_page

  def _set_results_per_page(self, rpp):
    self._results_per_page = rpp

  results_per_page = property(fset = _set_results_per_page, fget = _get_results_per_page)


  def get_results(self):
      """ Gets a page of results """
      # TODO
      if self.eor:
          return []
      MAX_VALUE = 100000000
      page = self._get_results_page()
      #search_info = self._extract_info(page)


      results = self._extract_results(page)
      search_info = {'from': self.results_per_page*self._page,
                     'to': self.results_per_page*self._page + len(results),
                     'total': MAX_VALUE}


      if not self.results_info:
          self.results_info = search_info
          if self.num_results == 0:
              self.eor = True
              return []
      if not results:
          self.eor = True
          return []
      if self._page > 0 and search_info['from'] == self._last_from:
          self.eor = True
          return []
      if search_info['to'] == search_info['total']:
          self.eor = True
      self._page += 1
      self._last_from = search_info['from']
      return results

  def _maybe_raise(self, cls, *arg):
      if self.debug:
          raise cls(*arg)

  def _get_results_page(self):
      if self._page == 0:
          if self._results_per_page == 10:
              url = GoogleSearch.SEARCH_URL_0
          else:
              url = GoogleSearch.SEARCH_URL_1
      else:
          if self._results_per_page == 10:
              url = GoogleSearch.NEXT_PAGE_0
          else:
              url = GoogleSearch.NEXT_PAGE_1

      safe_url = [url % { 'query': urllib.quote_plus(self.query),
                         'start': self._page * self._results_per_page,
                         'num': self._results_per_page,
                         'tld': self._tld,
                         'lang': self._lang,
                         'lang_restrict': self._lang_restrict
                        }]

      # possibly extend url with optional properties
      if self._first_indexed_in_previous:
          safe_url.extend(["&as_qdr=", self._first_indexed_in_previous])
      if self._filetype:
          safe_url.extend(["&as_filetype=", self._filetype])

      safe_url = "".join(safe_url)
      self._last_search_url = safe_url

      try:
          page = self.browser.get_page(safe_url)
      except BrowserError, e:
          raise SearchError, "Failed getting %s: %s" % (e.url, e.error)

      return BeautifulSoup(page)

  def _extract_info(self, soup):
      empty_info = {'from': 0, 'to': 0, 'total': 0}
      div_ssb = soup.find('div', id='ssb')
      if not div_ssb:
          self._maybe_raise(ParseError, "Div with number of results was not found on Google search page", soup)
          return empty_info
      p = div_ssb.find('p')
      if not p:
          self._maybe_raise(ParseError, """<p> tag within <div id="ssb"> was not found on Google search page""", soup)
          return empty_info
      txt = ''.join(p.findAll(text=True))
      txt = txt.replace(',', '')
      matches = re.search(r'%s (\d+) - (\d+) %s (?:%s )?(\d+)' % self._re_search_strings, txt, re.U)
      if not matches:
          return empty_info
      return {'from': int(matches.group(1)), 'to': int(matches.group(2)), 'total': int(matches.group(3))}

  def _extract_results(self, soup):
      results = soup.findAll('li', {'class': 'g'})
      ret_res = []
      for result in results:
          eres = self._extract_result(result)
          if eres:
              ret_res.append(eres)
      return ret_res

  def _extract_result(self, result):
      title, url = self._extract_title_url(result)
      desc = self._extract_description(result)
      #if not title or not url or not desc:
      #    return None
      return SearchResult(title, url, desc)

  def _extract_title_url(self, result):
      #title_a = result.find('a', {'class': re.compile(r'\bl\b')})
      title_a = result.find('a')
      if not title_a:
          self._maybe_raise(ParseError, "Title tag in Google search result was not found", result)
          return None, None
      title = ''.join(title_a.findAll(text=True))
      title = self._html_unescape(title)
      url = title_a['href']
      match = re.match(r'/url\?q=(http[^&]+)&', url)
      if match:
          url = urllib.unquote(match.group(1))
      return title, url

  def _extract_description(self, result):
      desc_div = result.find('div', {'class': re.compile(r'\bs\b')})
      if not desc_div:
          self._maybe_raise(ParseError, "Description tag in Google search result was not found", result)
          return None

      desc_strs = []
      def looper(tag):
          if not tag: return
          for t in tag:
              try:
                  if t.name == 'br': break
              except AttributeError:
                  pass

              try:
                  desc_strs.append(t.string)
              except AttributeError:
                  desc_strs.append(t)

      looper(desc_div)
      looper(desc_div.find('wbr')) # BeautifulSoup does not self-close <wbr>

      desc = ''.join(s for s in desc_strs if s)
      return self._html_unescape(desc)

  def _html_unescape(self, str):
      def entity_replacer(m):
          entity = m.group(1)
          if entity in name2codepoint:
              return unichr(name2codepoint[entity])
          else:
              return m.group(0)

      def ascii_replacer(m):
          cp = int(m.group(1))
          if cp <= 255:
              return unichr(cp)
          else:
              return m.group(0)

      s =    re.sub(r'&#(\d+);',  ascii_replacer, str, re.U)
      return re.sub(r'&([^;]+);', entity_replacer, s, re.U)




if __name__ == '__main__':
  kw = "Giochi on-line um Progressivo jackpot"

  gs = GoogleSearch(kw, lang="pt", lang_restrict="lang_pt")
  gs.results_per_page = 10
  results = gs.get_results()
  for result in results:
    if result.title:
      print result.title.encode('utf8')
    if result.url:
      print result.url.encode('utf8')
    if result.desc:
      print result.desc.encode('utf8')
    print
