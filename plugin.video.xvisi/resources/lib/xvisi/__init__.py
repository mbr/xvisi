from .vodly import Vodly

_all_sites = [
    Vodly(),
]

all_sites = {
    site.id: site for site in _all_sites
}
