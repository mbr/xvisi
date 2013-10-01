import re
from urlparse import urljoin, urlparse

from lxml.html import fromstring
import requests


def remove_whitespace(s):
    NO_WHITESPACE_PLEASE = re.compile('\s+')

    return NO_WHITESPACE_PLEASE.sub(' ', s).strip()


class PutlockerWsSourceParser(object):
    def can_parse(self, url):
        u = urlparse(url)

        return 'putlocker.ws' in u.netloc

    def get_video_url(self, url):
        resp = requests.post(url, data={'freeuser': 'yes'})
        return re.search(r"'(http://.*?/streams/.*?)'", resp.text).group(1)


class PutlockerComSourceParser(object):
    def can_parse(self, url):
        u = urlparse(url)

        return 'putlocker.ws' in u.netloc

    def get_video_url(self, url):
        resp = requests.post(url, data={'freeuser': 'yes'})
        return re.search(r"'(http://.*?/streams/.*?)'", resp.text).group(1)



def parse_vodly_result(page):
    root = fromstring(page)
    for link in root.cssselect('.index_item > a'):
        yield link.attrib['href'], link.text_content()


def parse_vodly_sources(page, baseurl):
    root = fromstring(page)
    for link in root.cssselect('table.movie_version .movie_version_link a'):
        link = link.attrib['href']

        if not link.startswith('/external.php'):
            continue

        resp = requests.get(urljoin(baseurl, link),
                            allow_redirects=False)
        yield resp.headers['location']


def parse_vodly_episodes(page, baseurl):
    root = fromstring(page)

    for h2_season in root.cssselect('.tv_container h2'):
        for elem in h2_season.itersiblings():
            if elem.tag == 'h2':
                break

            link = elem.cssselect('a')[0]
            title = '%s %s' % (
                remove_whitespace(h2_season.text_content()),
                remove_whitespace(link.text_content()),
            )

            yield link.attrib['href'], title


if __name__ == '__main__':
    source_parsers = [
        PutlockerSourceParser(),
    ]
    #TESTURL = ('http://vodly.to/index.php?search_keywords='
    #           'simpsons&search_section=1')

    #TESTURL = 'http://vodly.to/watch-1376-The-Simpsons-Movie'

    #TESTURL = ('http://vodly.to/tv-2363765-16-and-Pregnant')
    TESTURL = 'http://vodly.to/tv-2363765-16-and-Pregnant/season-1-episode-1'

    resp = requests.get(TESTURL)
    #for link, title in parse_vodly_episodes(resp.text, TESTURL):
    #    print link, title
    #print parse_vodly_sources(resp.text)

    #for link, title in parse_vodly_result(resp.text):
    #    print '%s: %s' % (title, link)

    for link in parse_vodly_sources(resp.text, TESTURL):
        for parser in source_parsers:
            if parser.can_parse(link):
                print parser.get_video_url(link)
