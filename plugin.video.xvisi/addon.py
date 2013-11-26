import os
import sys
import time

# hack around xbmc
sys.path.insert(0, os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'global'))

from xbmcswift2 import Plugin
from xbmcswift2 import xbmc, xbmcgui
import requests

try:
    import lxml
    lxml
except ImportError:
    dialog = xbmcgui.Dialog()
    dialog.ok('Sorry!', "Sorry, but you don't have lxml available and we",
                        "can't install it for you. Contact your xbmc-supplier",
                        "for a fix - or sneakily do it yourself!")
    import sys
    sys.exit(0)

from resources.lib.xvisi import all_sites, get_sources_for

plugin = Plugin()

_history = plugin.get_storage('search_history')
if not 'entries' in _history:
    _history['entries'] = []


DOWNLOAD_MOVIE_FN = os.path.join(
    xbmc.translatePath('special://temp'),
    'xvisi-video-tmp'
)
BUFSIZE = 1024 * 4


def format_delta(s):
    s = int(s)

    def pluralize(n, word):
        return '%d %s%s' % (
            n, word, 's' if n != 1 else ''
        )

    if s < 60:
        return pluralize(s, 'second')

    minutes = s / 60
    seconds = s % 60

    # 2-5 minutes return exact time
    if minutes < 5:
        return '%s, %s' % (pluralize(minutes, 'minute'),
                           pluralize(seconds, 'second'))

    if minutes < 60:
        return pluralize(minutes, 'minute')

    hours = minutes / 60
    minutes %= 60

    return '%s, %s' % (pluralize(hours, 'hour'),
                       pluralize(minutes, 'minute'))


@plugin.route('/')
def index():
    for site_id in sorted(all_sites.keys()):
        site = all_sites[site_id]

        yield {
            'label': site.name,
            'path': plugin.url_for('show_site', site_id=site.id),
        }

    for entry in _history['entries']:
        yield {
            'label': 'Search "%s"' % entry,
            'path': plugin.url_for('search', terms=entry)
        }

    yield {
        'label': 'Search all sites...',
        'path': plugin.url_for('show_search_form')
    }

    yield {
        'label': 'Play last download',
        'path': DOWNLOAD_MOVIE_FN,
        'is_playable': True,
    }


@plugin.route('/search/')
def show_search_form():
    keyboard = xbmc.Keyboard('')
    keyboard.doModal()
    if (keyboard.isConfirmed()):
        return plugin.redirect(plugin.url_for(
            'search', terms=keyboard.getText()
        ))
    return plugin.redirect(plugin.url_for('index'))


@plugin.route('/search/<terms>/')
def search(terms):
    if not all_sites:
        return []

    if terms in _history['entries']:
        _history['entries'].remove(terms)

    _history['entries'].insert(0, terms)
    _history['entries'] = _history['entries'][:10]

    progress = xbmcgui.DialogProgress()
    progress.create('Searching...', terms)

    results = []
    total = len(all_sites)
    for i, site in enumerate(all_sites.values()):
        for type, key, title in site.search(terms):
            if type == 'TVSHOW':
                results.append({
                    'label': '[%s] (TV) %s' % (site.short_name, title),
                    'path': plugin.url_for('show_tvshow',
                                           site_id=site.id,
                                           key=key)
                })
            elif type == 'MOVIE':
                results.append({
                    'label': '[%s] (Movie) %s' % (site.short_name, title),
                    'path': plugin.url_for('show_sources',
                                           site_id=site.id,
                                           key=key)
                })

        progress.update(int(100.0 * (i + 1) / total),
                        'Results so far: %d' % len(results),
                        '',
                        'Done searching %s' % site.name)
        if progress.iscanceled():
            break

    progress.close()

    return results


@plugin.route('/sites/<site_id>/')
def show_site(site_id):
    site = all_sites[site_id]

    for type, key, title in site.get_front():
        if type == 'TVSHOW':
            yield {
                'label': '(TV) %s' % title,
                'path': plugin.url_for('show_tvshow',
                                       site_id=site.id,
                                       key=key)
            }
        elif type == 'MOVIE':
            yield {
                'label': '(Movie) %s' % title,
                'path': plugin.url_for('show_sources',
                                       site_id=site.id,
                                       key=key)
            }


@plugin.route('/sites/sources/<site_id>/<key>/')
# do not use caching - often times, the plugin is updated to show
# newly added sources, causing the cache to display stale results
#@plugin.cached()
def show_sources(site_id, key):
    site = all_sites[site_id]

    sources = []
    for url, title in site.get_sources(key):
        for source in get_sources_for(url):
            sources.append({
                'label': title,
                'path': plugin.url_for('play_source', url=url)
            })

    # if there's only one sources, try to play immediately
    if len(sources) == 1:
        return plugin.redirect(sources[0]['path'])

    return sources


@plugin.route('/play/<url>/')
def play_source(url):
    source = get_sources_for(url)[0]
    video_url = source.get_video_url(url)

    # FIXME: maybe its possible to do this a little smarter and play directly?
    return [{
        'label': 'Play video',
        'path': video_url,
        'is_playable': True,
    }, {
        'label': 'Download and play',
        'path': plugin.url_for('download_and_play', url=video_url),
    }]


@plugin.route('/play-downloaded/')
def play_downloaded():
    return [{
        'label': 'Play downloaded file',
        'path': DOWNLOAD_MOVIE_FN,
        'is_playable': True,
    }]


@plugin.route('/buffered_play/<url>/')
def download_and_play(url):
    progress = xbmcgui.DialogProgress()
    progress.create('Starting download...')
    r = requests.get(url, stream=True)

    downloaded = 0
    total = r.headers['content-length']\
        if 'content-length' in r.headers else None

    with open(DOWNLOAD_MOVIE_FN, 'w') as outfile:
        start_time = time.time()
        for chunk in r.iter_content(chunk_size=BUFSIZE):
            outfile.write(chunk)
            downloaded += len(chunk)

            text = ['Downloaded %.2f M' % (downloaded / 1024.0 / 1024.0)]
            completion = 0

            if total:
                elapsed = time.time() - start_time
                completion = downloaded / float(total)

                if completion > 0:
                    remaining = elapsed / completion - elapsed
                    text.append('Time remaining: %s' %
                                format_delta(remaining))

            progress.update(int(completion) * 100, *text)

            if progress.iscanceled():
                break

    progress.close()
    return [{
        'label': 'Play download',
        'path': DOWNLOAD_MOVIE_FN,
        'is_playable': True,
    }]


@plugin.route('/sites/tvshow/<site_id>/seasons/<key>/')
def show_tvshow(site_id, key):
    site = all_sites[site_id]

    for key, title in site.get_seasons(key):
        yield {
            'label': title,
            'path': plugin.url_for('show_episodes',
                                   site_id=site.id,
                                   key=key)
        }


@plugin.route('/sites/tvshow/<site_id>/episodes/<key>/')
def show_episodes(site_id, key):
    site = all_sites[site_id]

    for key, title in site.get_episodes(key):
        yield {
            'label': title,
            'path': plugin.url_for('show_sources',
                                   site_id=site.id,
                                   key=key)
        }


if __name__ == '__main__':
    plugin.run()
