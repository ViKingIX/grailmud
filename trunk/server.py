"""Handles server initialisation and pulls some Twisted ropes."""
import logging
import grail2
from twisted.internet.protocol import Factory
from grail2.telnet import LoggerIn
from grail2.rooms import Room
from grail2.objects import MUDObject, TargettableObject

class ConnectionFactory(Factory):
    """The actual server factory."""

    protocol = LoggerIn

    def __init__(self, objstorethunk):
        grail2.instance._bind(self)
        self.objstore = objstorethunk()
        self.root = self.objstore.get_root()
        Room._instances = self.root['all_rooms']
        MUDObject._instances = self.root['all_objects']
        TargettableObject._name_registry = \
                                       self.root['targettable_objects_by_name']
    
    def buildProtocol(self, address):
        prot = self.protocol()
        prot.factory = self
        logging.debug("%r returned from Factory.buildProtocol." % prot)
        return prot

    @property
    def ticker(self):
        return self.root['ticker']

    @property
    def startroom(self):
        return self.root['startroom']

