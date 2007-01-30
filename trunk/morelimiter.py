import re

chunk_pattern = r"(.*\n){%d}|(.*\n){%d}.*"

def indnum(s, t, n):
    ind = 0
    for _ in range(n):
        #add one so we skip the one we just found
        ind = s.index(t, ind) + 1
    return ind

class MoreLimiter(object):

    def __init__(self, limit):
        self.limit = limit

    def chunk(self, data):
        return Chunker(self, data)

    def change_limit(self, limit):
        self.limit = limit

class Chunker(object):

    def __init__(self, limiter, data):
        self.limiter = limiter
        self.data = data
        #1 is added here to account for the line at the very end, which may
        #turn out to be empty.
        self.initial_lines = self.lines_left = data.count('\n') + 1

    def next(self):
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
