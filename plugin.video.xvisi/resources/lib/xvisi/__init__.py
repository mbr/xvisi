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
