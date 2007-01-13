"""The heartbeat of the MUD."""
import grail2
import logging
from twisted.internet.task import LoopingCall
import cgitb
import sys

class WaitingForTick(object):
    """An object that'll wait for a certain number of ticks then executes a
    given command.
    """
    def __init__(self, ticks, cmd):
        self.ticks = ticks
        self.cmd = cmd

    def __cmp__(self, other):
        return cmp(self.ticks, other.ticks)

    def tick(self, ticker):
        """Go through one tick."""
        self.ticks -= 1
        if not self.ticks:
            self.cmd()
        else:
            ticker.add_command(self)

    __call__ = tick

class Ticker(object):
    """The object that sets the core rate of the MUD."""

    def __init__(self, freq):
        self.freq = freq
        self.looper = LoopingCall(self.tick)
        self.doing = []

    def add_command(self, cmd):
        """Set a command to fire on the next tick."""
        logging.debug("Adding %r to the ticker queue." % cmd)
        self.doing.append(cmd)

    def tick(self):
        """Go through one tick."""
        doing = self.doing
        self.doing = []
        for cmd in doing:
            try:
                cmd()
            except:
                logging.error(cgitb.text(sys.exc_info()))
                #hm. we -could- reraise here, but I don't think it's the Right
                #Thing to do.
        grail2.instance.objstore.commit()

    def __getstate__(self):
        return {'doing': self.doing, 'freq': self.freq}

    def __setstate__(self, state):
        self.__dict__ = state
        self.looper = LoopingCall(self.tick)

    def start(self):
        """Commence the ticking."""
        self.looper.start(self.freq)

def doafter(time, cmd):
    """A handy shortcut for doing stuff after a certain amount of time. The
    first parameter is in seconds.
    """
    ticks = time / grail2.instance.ticker.freq
    grail2.instance.ticker.add_command(WaitingForTick(ticks, cmd))
