class VideoSite(object):
    name = 'Unnamed Site'  # long name to display
    id = 'und'             # internal id to be used
    shortname = 'unnmd'    # shorter name (use as part of other strings)

    def search(self, term):
        """Find results relating to search term, returns an iterator of
        results.

        Each result is a 3-tuple of (item_type, key, title)."""
        raise NotImplementedError()

    def get_front(self):
        """Like search(), but returns a random iterator of content, typically
        recently added items."""
        raise NotImplementedError()

    def get_sources(self, key):
        """Called with either a movie key or an episode key, returns
        a list of (url, title) links."""
        raise NotImplementedError()


class VideoSource(object):
    def can_play(self, url):
        raise NotImplementedError()

    def get_video_url(self, url):
        raise NotImplementedError()