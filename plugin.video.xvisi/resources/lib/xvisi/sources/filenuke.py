import re

from ..base import VideoSource
from ..web import web


class FileNukeSource(VideoSource):
    _NETLOC = 'filenuke.'

    def get_video_url(self, url):
        fnid = url[url.rfind('/'):]

        resp = web.post(url, data={
            'op': 'download1',
            'usr_login': '',
            'id': fnid,
            'fname': 'dl',
            'referer': '',
            'method_free': 'Play Now',
        })

        return re.search(r"'file', '(.*)'", resp.text).group(1)
