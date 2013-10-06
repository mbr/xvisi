import re

from ..base import VideoSource
from ..web import web


class FileNukeSource(VideoSource):
    _NETLOC = 'filenuke.'

    def get_video_url(self, url):
        fnid = url[url.rfind('/')+1:]

        resp = web.post(url, data={
            'op': 'download1',
            'usr_login': '',
            'id': fnid,
            'fname': 'dl',
            'referer': '',
            'method_free': 'Free',
            'fname': 'meh',
        })

        return re.search(r"'file', '(.*)'", resp.text).group(1)
