import re
from urlparse import urljoin

from lxml.html import fromstring

from ..base import VideoSource
from ..web import web


class PutlockerWsSource(VideoSource):
    _NETLOC = 'putlocker.ws'

    def get_video_url(self, url):
        resp = web.post(url, data={'freeuser': 'yes'})
        return re.search(r"'(http://.*?/streams/.*?)'", resp.text).group(1)


class PutlockerComSource(VideoSource):
    _NETLOC = 'putlocker.com'

    def can_play(self, url):
        return super(PutlockerComSource, self).can_play(url) and \
            not url.endswith('?404')

    def get_video_url(self, url):
        resp = web.post(url, data={'freeuser': 'yes'})

        # landiong page, get hash
        root = fromstring(resp.text)
        hash = root.cssselect('input[name=hash]')[0].attrib['value']

        resp = web.post(
            url,
            data={'hash': hash, 'confirm': 'Continue as Free User'}
        )

        root = fromstring(resp.text)

        # not supported by lxml version in system-wide use?
        #relurl = root.cssselect(
        #    'a:contains("Download File")'
        #)[0].attrib['href']

        for a in root.cssselect('a'):
            href = a.attrib.get('href')

            if href and href.startswith('/get_file.php'):
                return urljoin(url, href)
