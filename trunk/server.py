"""Handles server initialisation and pulls some Twisted ropes."""
import logging
from twisted.internet.protocol import Factory
from grail2.telnet import LoggerIn
from grail2.rooms import Room
from grail2.objects import PlayerCatalogue, TargettableObject
from grail2.npcs.chatty import ChattyNPC
from twisted.internet.task import LoopingCall
from grail2.ticks import Ticker
from bisect import insort

def startroom():
    """Returns a new room that the players are dumped into initially."""
    room = Room('An unremarkable moor.',
                'This moor is extremely bare. Overly so, perhaps. There '
                'is a definite air of blandness about its grey horizon '
                'and overcast sky. The ground is anonymous and blank; '
                'grey dust litters the floor, and that is about all which '
                'can be said about it. Even the air seems to be steeped in'
                ' mediocrity - a lukewarm temperature, with no discernable'
                ' exciting scents.')
    eliza = TargettableObject('a bespectacled old lady', 'Eliza',
                              set(['old', 'lady', 'woman']), room)
    eliza.addListener(ChattyNPC(eliza))
    room.add(eliza)
    return room

class ConnectionFactory(Factory):
    """The actual server factory."""

    protocol = LoggerIn

    def __init__(self, freq, *args, **kwargs):
        self.room = startroom()
        self.catalogue = PlayerCatalogue()
        self.ticker = Ticker()
        self.looper = LoopingCall(self.ticker.tick)
        self.looper.start(freq)
    
    def buildProtocol(self, address):
        prot = self.protocol(self.room, self.catalogue, self.ticker)
        prot.factory = self
        logging.debug("%r returned from Factory.buildProtocol." % prot)
        return prot

