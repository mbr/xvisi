from .sites import vodly, primewire
from .sources import putlocker, filenuke

_all_sites = [
    vodly.Vodly(),
    primewire.PrimeWire(),
]

all_sources = [
    putlocker.PutlockerComSource(),
    putlocker.PutlockerWsSource(),
    filenuke.FileNukeSource(),
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
