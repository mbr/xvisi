from urlparse import urlparse, urljoin

from lxml.html import fromstring

from .vodly import Vodly
from ..web import web


class PrimeWire(Vodly):
    _BASEURL = 'http://www.primewire.ag'
    name = 'PrimeWire.ag'
    short_name = 'primewire'
    id = 'primewire'

    def get_sources(self, key):
        resp = web.get(key)

        root = fromstring(resp.text)

        for link in root.cssselect(
            'table.movie_version .movie_version_link a'
        ):
            link = link.attrib['href']

            if not link.startswith('/external.php'):
                continue

            # FIXME: could check for redirects here
            resp = web.get(urljoin(self._BASEURL, link))

            if not resp.url.startswith(self._BASEURL):
                # we got the url directly, rejoice
                yield resp.url, urlparse(resp.url).netloc

            exroot = fromstring(resp.text)

            # get last frame's href
            frames = exroot.cssselect('frame')
            if not frames:
                # not a source site (no frames)
                continue

            href = frames[-1].attrib['src']
            yield href, urlparse(href).netloc

    def get_front(self):
        for url, type in [(self._BASEURL, 'MOVIE'),
                          (self._BASEURL + '?tv', 'TVSHOW')]:
            resp = web.get(url)

            for item in self._parse_overview(resp.text):
                yield type, item['link'], item['title']
