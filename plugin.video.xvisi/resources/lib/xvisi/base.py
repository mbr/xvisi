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
        pass
