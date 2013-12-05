from lxml.html import fromstring

from ..base import VideoSource, VideoSourceRemovedError
from ..web import web


class PromptFileSource(VideoSource):
    _NETLOC = 'promptfile.com'

    def get_video_url(self, url):
        buf = web.get(url).text
        if ('The file you requested does not exist '
           'or has been removed') in buf:
            raise VideoSourceRemovedError('The video has been deleted.')

        root = fromstring(buf)

        chash = root.cssselect('input[name="chash"]')[0].attrib['value']

        resp = web.post(url, data={
            'chash': chash,
        })

        root = fromstring(resp.text)
        return root.cssselect('a.view_dl_link')[0].attrib['href']
