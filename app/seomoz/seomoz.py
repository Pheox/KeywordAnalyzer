#!/usr/bin/env python
# -*- coding: utf-8 -*-



"""
API example:


from seomoz import Seomoz

sm = Seomoz('member-cb8c6a3545', '08b3fd7453bdf1e7b452ea09b1174ff2')
metrics = sm.urlMetrics('www.seomoz.org')

metrics = l.urlMetrics(['www.seomoz.org', 'www.seomoz.org/blog'])
authorities = l.urlMetrics(['www.seomoz.org'], lsapi.UMCols.domainAuthority | lsapi.UMCols.pageAuthority)



TODO's:
-  1. Seomoz class
-  Proxy class - !!
-  simple/intuitive API
-  meaning of used libraries
-  free version supports only "URLmetrics" and "Links"
-  Moz Analytics account - higher rate (1 query every 5 seconds)
-  free columns are implicit
-  links OK?, links needed ?? - links have useful info i think !!
-  edit header of this script - correct API example, author, licence etc.!
needed:
- metrics: domain_authority (pda), page_authority (upa), moz_rank(umrp, umrr)
"""

import hashlib # sha1
import hmac # hash message authentication code
import time
import base64
import urllib
import urllib2
try:
  import simplejson as json
except:
  import json


class SeomozException(Exception):
  """ An error messages wrapper. """
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return str(self.value)
  def __repr__(self):
    return repr(self.value)



class Seomoz:
  """ Class implementing Mozscape API"""

  class MetricCols:
    '''UrlMetric colums'''
    # Flags for urlMetrics
    # Title of page if available
    title             = 1 # ut
    # Canonical form of the url
    url               = 4 # uu
    # The subdomain of the url
    subdomain         = 8 # ufq
    # The root domain of the url
    root_domain        = 16 # upl
    # The number of juice-passing external links to the url
    external_links       = 32 # ueid
    # The number of juice-passing external links to the subdomain
    subdomain_external_links  = 64 # feid
    # The number of juice-passing external links
    root_domain_external_links = 128 # peid
    # The number of juice-passing links (internal or external) to the url
    juice_passing_links     = 256 # ujid
    # The number of subdomains with any pages linking to the url
    subdomains_linking     = 512 # uifq
    # The number of root domains with any pages linking to the url
    root_domains_linking    = 1024 # uipl
    # The number of links (juice-passing or not, internal or external) to the url
    links           = 2048 # uid
    # The number of subdomains with any pages linking to the subdomain of the url
    subdomain_subdomains_Linking = 4096 # fid
    # The number of root domains with any pages linking to the root domain of the url
    root_domain_root_domains_linking = 8192 # pid
    # The mozRank of the url.  Requesting this metric will provide both the
    # pretty 10-point score (in umrp) and the raw score (umrr)
    moz_rank         = 16384 # umrp, umrr
    # The mozRank of the subdomain of the url. Requesting this metric will
    #provide both the pretty 10-point score (fmrp) and the raw score (fmrr)
    subdomain_moz_rank    = 32768 # fmrp, fmrr
    # The mozRank of the Root Domain of the url. Requesting this metric will
    # provide both the pretty 10-point score (pmrp) and the raw score (pmrr)
    root_domain_moz_rank     = 65536 # pmrp, pmrr
    # The mozTrust of the url. Requesting this metric will provide both the
    # pretty 10-point score (utrp) and the raw score (utrr).
    moz_trust        = 131072 # utrp, utrr
    # The mozTrust of the subdomain of the url.  Requesting this metric will
    # provide both the pretty 10-point score (ftrp) and the raw score (ftrr)
    subdomain_moz_trust     = 262144 # ftrp, ftrr
    # The mozTrust of the root domain of the url.  Requesting this metric
    # will provide both the pretty 10-point score (ptrp) and the raw score (ptrr)
    root_domain_moz_trust    = 524288 # ptrp, ptrr
    # The portion of the url's mozRank coming from external links.  Requesting
    # this metric will provide both the pretty 10-point score (uemrp) and the raw
    # score (uemrr)
    external_moz_rank     = 1048576 # uemrp, uemrr
    # The portion of the mozRank of all pages on the subdomain coming from
    # external links.  Requesting this metric will provide both the pretty
    # 10-point score (fejp) and the raw score (fejr)
    subdomain_external_domain_juice = 2097152  # fejp, fejr
    # The portion of the mozRank of all pages on the root domain coming from
    # external links.  Requesting this metric will provide both the pretty
    # 10-point score (pejp) and the raw score (pejr)
    root_domain_external_domain_juice = 4194304 # pejp, pejr
    # The mozRank of all pages on the subdomain combined.  Requesting this
    # metric will provide both the pretty 10-point score (fjp) and the raw score (fjr)
    subdomain_domain_juice  = 8388608 # fjp, fjr
    # The mozRank of all pages on the root domain combined.  Requesting this
    # metric will provide both the pretty 10-point score (pjp) and the raw score (pjr)
    root_domain_domain_juice   = 16777216 # pjp, pjr
    # The HTTP status code recorded by Linkscape for this URL (if available)
    http_status_code      = 536870912 # us
    # Total links (including internal and nofollow links) to the subdomain of
    # the url in question
    links_to_subdomain    = 4294967296 # fuid
    # Total links (including internal and nofollow links) to the root domain
    # of the url in question.
    links_to_root_domain     = 8589934592 # puid
    # The number of root domains with at least one link to the subdomain of
    # the url in question
    root_domains_linking_to_subdomain = 17179869184 # fipl
    # A score out of 100-points representing the likelihood for arbitrary content
    # to rank on this page
    page_authority       = 34359738368 # upa
    # A score out of 100-points representing the likelihood for arbitrary content
    # to rank on this dom
    domain_authority     = 68719476736 # pda

    # This is the set of all free fields
    freeCols = (title |
      url |
      external_links |
      links |
      moz_rank |
      subdomain_moz_rank |
      http_status_code |
      page_authority |
      domain_authority)

  class AnchorCols:
    '''Anchor Text Cols'''
    # The anchor text term or phrase
    term          = 2 # *t
    # The number of internal pages linking with this term or phrase
    internal_pages_linking  = 8 # *iu
    # The number of subdomains on the same root domain with at least one link with this term or phrase
    internal_subdomains_linking = 16 # *if
    # The number of external pages linking with this term or phrase
    external_pages_linking  = 32 # *eu
    # The number of external subdomains with at least one link with this term or phrase
    external_subdomains_linking = 64 # *ef
    # The number of (external) root domains with at least one link with this term or phrase
    external_root_domains_linking = 128 # *ep
    # The amount of mozRank passed over all internal links with this term or phrase (on the 10 point scale)
    internal_moz_rank_passed   = 256 # *imp
    # The amount of mozRank passed over all external links with this term or phrase (on the 10 point scale)
    external_moz_rank_passed   = 512 # *emp
    # Currently only "1" is used to indicate the term or phrase is found in an image link
    flags           = 1024 # *f

    # This is the set of all free fields
    freeCols = (term |
      internal_pages_linking |
      internal_subdomains_linking |
      external_pages_linking |
      external_subdomains_linking |
      external_root_domains_linking |
      internal_moz_rank_passed |
      external_moz_rank_passed |
      flags)

  # The base url we request from
  base = 'http://lsapi.seomoz.com/linkscape/%s?%s'

  def __init__(self, access_id, secret_key):
    self.access_id  = access_id
    self.secret_key = secret_key

  def signature(self, expires):
    to_sign  = '%s\n%i' % (self.access_id, expires)
    return base64.b64encode(hmac.new(self.secret_key, to_sign, hashlib.sha1).digest())

  def query(self, method, data=None, **params):
    expires = int(time.time() + 300)
    params['AccessID' ] = self.access_id
    params['Expires'  ] = expires
    params['Signature'] = self.signature(expires)
    request = Seomoz.base % (method.encode('utf-8'), urllib.urlencode(params))
    try:
      return json.loads(urllib2.urlopen(request, data).read())
    except urllib2.HTTPError as e:
      # The unauthorized status code can sometimes have meaningful data
      if e.code == 401:
        raise SeomozException(e.read())
      else:
        raise SeomozException(e)
    except Exception as e:
      raise SeomozException(e)

  def urlMetrics(self, urls, cols=MetricCols.freeCols):
    # TODO! Create proxy
    q = None
    if isinstance(urls, basestring):
      q = self.query('url-metrics/%s' % urllib.quote(urls), Cols=cols)
    else:
      q = self.query('url-metrics', data=json.dumps(urls), Cols=cols)
    time.sleep(11)
    return q

  def anchorText(self, url, scope='phrase_to_page', sort='domains_linking_page', cols=AnchorCols.freeCols):
    return self.query('anchor-text/%s' % urllib.quote(url), Scope=scope, Sort=sort, Cols=cols)

  def links(self, url, scope='page_to_page', sort='page_authority', filters=['internal'],
    target_cols=(MetricCols.url | MetricCols.page_authority),
    source_cols=(MetricCols.url | MetricCols.page_authority),
    link_cols  =(MetricCols.url | MetricCols.page_authority)):
    '''This is currently broken. Have not figured it out'''
    return self.query('links/%s' % urllib.quote(url),
      Scope      = scope,
      Sort       = sort,
      Filter     = '+'.join(filters),
      TargetCols = target_cols,
      SourceCols = source_cols,
      linkCols   = link_cols)

### Testing MAIN ###

if __name__ == '__main__':

  sm = Seomoz('member-cb8c6a3545', '08b3fd7453bdf1e7b452ea09b1174ff2')
  metrics = Seomoz.MetricCols.domain_authority|Seomoz.MetricCols.page_authority|Seomoz.MetricCols.moz_rank

  #results = sm.urlMetrics(['http://cs.wikipedia.org/wiki/Eminem'], metrics)
  #results = sm.urlMetrics(['http://cs.wikipedia.org'], metrics)
  #results = sm.urlMetrics(['http://cs.wikipedia.org', 'http://cs.wikipedia.org/wiki/Eminem'], metrics)
  #results = sm.urlMetrics(['cs.wikipedia.org', 'cs.wikipedia.org/wiki/Eminem'],metrics)
  results = sm.urlMetrics(['http://www1.macys.com/shop/shoes?id=13247', 'http://www1.macys.com/shop/shoes', 'http://www1.macys.com'], metrics)
  print results
