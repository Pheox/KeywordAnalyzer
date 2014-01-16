#!/usr/bin/env python

# Google Pagerank Checksum Algorithm (Firefox Toolbar)
# Downloaded from http://pagerank.phurix.net/
# Requires: Python >= 2.4


import httplib
import urllib
import urllib2


def getHash(query):
  seed = "Mining PageRank is AGAINST GOOGLE'S TERMS OF SERVICE. Yes, I'm talking to you, scammer."
  result = 0x01020345

  for i in range(len(query)):
    result ^= ord(seed[i%len(seed)]) ^ ord(query[i])
    result = result >> 23 | result << 9
    result &= 0xffffffff

  return '8%x' % result

def getPageRank(url):
  """ Returns PageRank for a specified URL. """

  #headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:22.0) Gecko/20100101 Firefox/22.0'}
  conn = httplib.HTTPConnection('toolbarqueries.google.com')
  h = getHash(url)
  path = '/tbr?client=navclient-auto&ch=%s&features=Rank&q=info:%s' % (h, url)
  conn.request('GET', path)
  response = conn.getresponse()
  data = response.read().strip()
  conn.close()
  try:
    return int(data.split(":")[-1])
  except ValueError:
    return -1


def getSRank(url):
  """ Returns S-Rank for specified URL. """
  url = urllib.quote(url)
  result = urllib2.urlopen('http://srank.seznam.cz/?url=' + url)

  if result is not None:
    rank = result.read()
    result.close()
    return int(rank)
  return 0



##### MAIN #####

if __name__ == '__main__':
  url = 'http://forums.lotro.com/showthread.php?495440-Kundi-Items-aus-Inis-und-M%FCtzeln'
  url = urllib.quote(url)

  print 'PR for %s is %d' % (url, getPageRank(url))
  print 'S-Rank for %s is %d' % (url, getSRank(url))
