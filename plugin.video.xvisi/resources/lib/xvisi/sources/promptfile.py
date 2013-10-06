from lxml.html import fromstring

from ..base import VideoSource
from ..web import web


class PromptFileSource(VideoSource):
    _NETLOC = 'promptfile.com'

    def get_video_url(self, url):
        root = fromstring(web.get(url).text)

        chash = root.cssselect('input[name="chash"]')[0].attrib['value']

        resp = web.post(url, data={
            'chash': chash,
        })

        root = fromstring(resp.text)
        return root.cssselect('a.view_dl_link')[0].attrib['href']
