from xbmcswift2 import Plugin
from resources.lib.xvisi import all_sites

plugin = Plugin()


@plugin.route('/')
def index():
    for site_id in sorted(all_sites.keys()):
        site = all_sites[site_id]

        yield {
            'label': site.name,
            'path': plugin.url_for('show_site', site_id=site.id),
            'is_playable': False,
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
                'path': plugin.url_for('show_movie',
                                       site_id=site.id,
                                       key=key)
            }


@plugin.route('/sites/movie/<site_id>/<key>/')
def show_movie(site_id, url):
    return []


@plugin.route('/sites/tvshow/<site_id>/<key>/')
def show_tvshow(site_id, url):
    return []


if __name__ == '__main__':
    plugin.run()
