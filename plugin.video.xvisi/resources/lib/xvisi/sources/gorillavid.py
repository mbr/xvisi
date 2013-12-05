import re

from ..base import VideoSource, VideoSourceRemovedError
from ..web import web


class GorillaVidSource(VideoSource):
    _NETLOC = 'gorillavid.in'
    _URL_ID = re.compile('.*/([0-9a-z]+)/?')
    _VIDEO_FILE_RE = re.compile('(http://.*?/video.flv)')

    def get_video_url(self, url):
        # get the id from the url
        file_id = self._URL_ID.match(url).group(1)
        buf = web.post(url, data={
            'op': 'download1',
            'id': file_id,
            'method_free': 'Free Download',
        }).text
        if ('File Not Found') in buf:
            raise VideoSourceRemovedError('The video has been deleted.')

        return str(self._VIDEO_FILE_RE.search(buf).groups(1))
