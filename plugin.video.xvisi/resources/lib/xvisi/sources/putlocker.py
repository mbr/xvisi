import re
from urlparse import urlparse

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
        raise NotImplementedError('ooops')
