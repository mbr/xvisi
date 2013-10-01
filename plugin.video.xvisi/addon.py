from xbmcswift2 import Plugin
from resources.lib.xvisi import all_sites, get_sources_for

plugin = Plugin()


@plugin.route('/')
def index():
    for site_id in sorted(all_sites.keys()):
        site = all_sites[site_id]

        yield {
            'label': site.name,
            'path': plugin.url_for('show_site', site_id=site.id),
        }


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

    return [{
        'label': 'Play',
        'path': video_url,
        'is_playable': True,
    }]


@plugin.route('/sites/tvshow/<site_id>/<key>/')
def show_tvshow(site_id, url):
    return []


if __name__ == '__main__':
    plugin.run()
