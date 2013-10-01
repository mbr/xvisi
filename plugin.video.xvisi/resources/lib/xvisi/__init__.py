from .sites import vodly
from .sources import putlocker

_all_sites = [
    vodly.Vodly(),
]

all_sources = [
    putlocker.PutlockerComSource(),
    putlocker.PutlockerWsSource(),
]

all_sites = {
    site.id: site for site in _all_sites
}


def get_sources_for(url):
    sources = []
    for source in all_sources:
        if source.can_play(url):
            sources.append(source)

    return sources
