import re
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


def remove_whitespace(s):
    NO_WHITESPACE_PLEASE = re.compile('\s+')

    return NO_WHITESPACE_PLEASE.sub(' ', s).strip()


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

    def get_episodes(self, key):
        resp = web.get(key)

        root = fromstring(resp.text)

        for h2_season in root.cssselect('.tv_container h2'):
            episodes = []

            for elem in h2_season.itersiblings():
                if elem.tag == 'h2':
                    break

                if 'transp2' in elem.attrib['class']:
                    # unavailable episode
                    continue

                link = elem.cssselect('a')[0]
                episodes.append((
                    link.attrib['href'],
                    remove_whitespace(link.text)
                ))

            yield remove_whitespace(h2_season.cssselect('a')[0].text), episodes

    def get_front(self):
        for url in (self._BASEURL, self._BASEURL + '?tv'):
            resp = web.get(url)

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
                'link': urljoin(self._BASEURL, link.attrib['href']),
                'title': link.attrib['title'],
            }

            if d['title'].startswith('Watch '):
                d['title'] = d['title'][6:]

            yield d
