"""Handles server initialisation and pulls some Twisted ropes."""
import logging
import grail2
from twisted.internet.protocol import Factory
from grail2.telnet import LoggerIn
from grail2.objects import PlayerCatalogue

class ConnectionFactory(Factory):
    """The actual server factory."""

    protocol = LoggerIn

    def __init__(self, objstorethunk):
        #ideally, the next line would be in rungrail.py, but Durus is too
        #eager.
        grail2.instance = self
        self.catalogue = PlayerCatalogue()
        self.objstore = objstorethunk()
    
    def buildProtocol(self, address):
        prot = self.protocol(self.startroom, self.catalogue, self.ticker)
        prot.factory = self
        logging.debug("%r returned from Factory.buildProtocol." % prot)
        return prot

    @property
    def ticker(self):
        return self.objstore.get_root()['ticker']

    @property
    def startroom(self):
        return self.objstore.get_root()['startroom']

