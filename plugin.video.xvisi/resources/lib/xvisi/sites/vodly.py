from urlparse import urljoin, urlparse

from lxml.html import fromstring

from ..base import VideoSite
from ..web import web


def _get_link_type(link):
    u = urlparse(link)

    if u.path.startswith('/watch'):
        return 'MOVIE'
    elif u.path.startswith('/tv'):
        return 'TVSHOW'
    else:
        raise ValueError('Cannot get link type of %r' % link)


class Vodly(VideoSite):
    name = 'Vodly.to'
    short_name = 'vodly'
    id = 'vodly'

    _BASEURL = 'http://vodly.to/'

    def search(self, term):
        resp = web.get(urljoin(self._BASEURL, 'index.php'), params={
            'search_section': 1,
            'search_keywords': term,
        })

        for item in self._parse_overview(resp.text):
            yield _get_link_type(item['link']), item['link'], item['title']

    def get_front(self):
        resp = web.get(self._BASEURL)

        for item in self._parse_overview(resp.text):
            yield _get_link_type(item['link']), item['link'], item['title']

    def get_sources(self, key):
        resp = web.get(key)

        root = fromstring(resp.text)

        for link in root.cssselect(
            'table.movie_version .movie_version_link a'
        ):
            link = link.attrib['href']

            if not link.startswith('/external.php'):
                continue

            resp = web.get(urljoin(self._BASEURL, link),
                           allow_redirects=False)

            u = urlparse(resp.headers['location'])
            yield resp.headers['location'], u.netloc

    def _parse_overview(self, page):
        root = fromstring(page)
        for link in root.cssselect('.index_item > a'):
            d = {
                'link': link.attrib['href'],
                'title': link.attrib['title'],
            }

            if d['title'].startswith('Watch '):
                d['title'] = d['title'][6:]

            yield d
