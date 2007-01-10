# pylint: disable-msg=E1101
#twisted does some hackery with the reactor that pylint doesn't know about.
"""This module is intended to be the main entry point for the server, run from
the shell.
"""
import grail2
from grail2.server import ConnectionFactory
from twisted.internet import reactor
import sys
import logging

logging.basicConfig(level = logging.DEBUG,
                    format = '%(asctime)s %(levelname)s %(message)s',
                    stream = sys.stdout)

def construct_mud(tickfreq):
    """Construct a MUD factory."""
    return ConnectionFactory(tickfreq)

def run_mud(mud, port):
    """Run the MUD factory."""
    reactor.listenTCP(port, mud)
    grail2.instance = mud
    reactor.run()

if __name__ == '__main__':
    run_mud(construct_mud(100), 6666)
