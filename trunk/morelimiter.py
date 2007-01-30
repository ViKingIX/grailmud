import re

chunk_pattern = r"(.*\n){%d}|(.*\n){%d}.*"

def indnum(string, target, num):
    """Find the index of the num-th occurence of target in string.

    Raises ValueErrors if there aren't enough targets."""
    ind = 0
    for _ in range(num):
        #add so we skip the one we just found
        ind = string.index(target, ind) + len(target)
    return ind

class MoreLimiter(object):
    """A recorder of what the limit is, and a producer of Chunkers that actually
    limit the data.
    """

    def __init__(self, limit):
        self.limit = limit

    def chunk(self, data):
        """Return a Chunker that limits the data."""
        return Chunker(self, data)

    def change_limit(self, limit):
        """Change the limit.

        Tihs affects already-created Chunkers.
        """
        self.limit = limit

class Chunker(object):
    """The object that actually does the chunking."""

    def __init__(self, limiter, data):
        self.limiter = limiter
        self.data = data
        #1 is added here to account for the line at the very end, which may
        #turn out to be empty.
        self.initial_lines = self.lines_left = data.count('\n') + 1

    def next(self):
        """Return the next chunk, a string with a set number of lines."""
        if not self.lines_left:
            raise StopIteration()
        try:
            nl_ind = indnum(self.data, "\n", self.limiter.limit)
        except ValueError: #not enough lines left!
            self.lines_left = 0
            res = self.data
        else: #we have more lines than the present limit
            res = self.data[:nl_ind]
            self.data = self.data[nl_ind:]
            self.lines_left -= self.limiter.limit
        return res

    def __iter__(self):
        return self
