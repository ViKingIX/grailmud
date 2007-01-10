class WaitingForTick(object):
    #XXX: needs some way to get itself known to the Ticker.

    def __init__(self, ticks, cmd):
        self.ticks = ticks
        self.cmd = cmd

    def __cmp__(self, other):
        return cmp(self.ticks, other.ticks)

    def tick(self, ticker):
        self.ticks -= 1
        if not self.ticks:
            ticker.add_command(self.cmd)
        else:
            ticker.add_command(self)

    __call__ = tick

class Ticker(object):

    def __init__(self):
        self.doing = []

    def add_command(self, cmd):
        self.doing.append(cmd)

    def tick(self):
        doing = self.doing
        self.doing = []
        for cmd in doing:
            cmd()
