from xbmcswift2 import Plugin
from xbmcswift2 import xbmc, xbmcgui

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

        progress.update(int(100.0 * (i+1) / total),
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
@plugin.cached()
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
    }]


@plugin.route('/sites/tvshow/<site_id>/<key>/')
def show_tvshow(site_id, key):
    site = all_sites[site_id]

    for season, episodes in site.get_episodes(key):
        for key, title in episodes:
            yield {
                'label': '%s/%s' % (season, title),
                'path': plugin.url_for('show_sources',
                                       site_id=site.id,
                                       key=key)
            }


if __name__ == '__main__':
    plugin.run()
