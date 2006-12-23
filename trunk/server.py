import logging
from twisted.internet.protocol import Factory
from grail2.telnet import LoggerIn
from grail2.rooms import Room

class ConnectionFactory(Factory):

    protocol = LoggerIn
    startroom = Room('An unremarkable moor.',
                     'This moor is extremely bare. Overly so, perhaps. There '
                     'is a definite air of blandness about its grey horizon '
                     'and overcast sky. The ground is anonymous and blank; '
                     'grey dust litters the floor, and that is about all which '
                     'can be said about it. Even the air seems to be steeped in'
                     ' mediocrity - a lukewarm temperature, with no discernible'
                     ' exciting scents.')

    def buildProtocol(self, address):
        prot = Factory.buildProtocol(self, address)
        logging.debug("%r returned from Factory.buildProtocol." % prot)
        prot.startroom = self.startroom
        return prot
