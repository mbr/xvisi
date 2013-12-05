from .sites import vodly, primewire
from .sources import putlocker, filenuke, promptfile, gorillavid

_all_sites = [
    vodly.Vodly(),
    primewire.PrimeWire(),
]

all_sources = [
    putlocker.PutlockerComSource(),
    putlocker.PutlockerWsSource(),
    promptfile.PromptFileSource(),
    gorillavid.GorillaVidSource(),
    # currently broken
    #filenuke.FileNukeSource(),
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
