from urlparse import urljoin, urlparse

from lxml.html import fromstring

from .base import VideoSite
from .web import web


class Vodly(VideoSite):
    _BASEURL = 'http://vodly.to/'

    def search(self, term):
        resp = web.get(urljoin(self._BASEURL, 'index.php'), params={
            'search_section': 1,
            'search_keywords': term,
        })

        for item in self._parse_overview(resp.text):
            yield item, item['title']

    def get_front(self):
        resp = web.get(self._BASEURL)

        for item in self._parse_overview(resp.text):
            yield item, item['title']

    def _parse_overview(self, page):
        root = fromstring(page)
        for link in root.cssselect('.index_item > a'):
            d = {
                'link': link.attrib['href'],
                'title': link.attrib['title'],
            }

            if d['title'].startswith('Watch '):
                d['title'] = d['title'][6:]

            u = urlparse(d['link'])
            if u.path.startswith('/watch'):
                d['vtype'] = 'MOVIE'
            elif u.path.startswith('/tv'):
                d['vtype'] = 'TVSHOW'
            else:
                raise ValueError('Could not identify link: %s' % link)

            yield d
