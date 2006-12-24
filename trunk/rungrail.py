"""This module is intended to be the main entry point for the server, run from
the shell.
"""
from grail2.server import ConnectionFactory
from twisted.internet import reactor
import sys
import logging

logging.basicConfig(level = logging.DEBUG,
                    format = '%(asctime)s %(levelname)s %(message)s',
                    stream = sys.stdout)

reactor.listenTCP(6666, ConnectionFactory())

reactor.run()
