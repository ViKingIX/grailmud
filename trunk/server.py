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

class ConnectionFactory(Factory):
    """The actual server factory."""

    protocol = LoggerIn

    def __init__(self, freq, objstore, startroom, *args, **kwargs):
        self.startroom = startroom
        self.catalogue = PlayerCatalogue()
        self.ticker = Ticker(objstore)
        self.looper = LoopingCall(self.ticker.tick)
        self.looper.start(freq)
        self.objstore = objstore
    
    def buildProtocol(self, address):
        prot = self.protocol(self.startroom, self.catalogue, self.ticker)
        prot.factory = self
        logging.debug("%r returned from Factory.buildProtocol." % prot)
        return prot

