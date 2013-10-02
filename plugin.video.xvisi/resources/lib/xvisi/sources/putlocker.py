import re
from urlparse import urlparse, urljoin

from lxml.html import fromstring

from ..base import VideoSource
from ..web import web


class PutlockerWsSource(VideoSource):
    def can_play(self, url):
        u = urlparse(url)

        return 'putlocker.ws' in u.netloc

    def get_video_url(self, url):
        resp = web.post(url, data={'freeuser': 'yes'})
        return re.search(r"'(http://.*?/streams/.*?)'", resp.text).group(1)


class PutlockerComSource(VideoSource):
    def can_play(self, url):
        u = urlparse(url)

        return 'putlocker.com' in u.netloc

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
