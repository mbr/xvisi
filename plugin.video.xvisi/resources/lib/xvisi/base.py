class VideoSite(object):
    name = 'Unnamed Site'  # long name to display
    shortname = 'unnmd'    # shorter name (use as part of other strings)

    def search(self, term):
        """Find results relating to search term, returns an iterator of
        results.

        Each result is a 2-tuple, the first object a key structure that is
        passed back to the Site (opaque to the user) and the second containing
        information for displaying the result."""
        raise NotImplementedError()

    def get_front(self):
        """Like search(), but returns a random iterator of content, typically
        recently added items."""
        pass
