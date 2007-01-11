# pylint: disable-msg=E1101
#twisted does some hackery with the reactor that pylint doesn't know about.
"""This module is intended to be the main entry point for the server, run from
the shell.
"""
from durus.file_storage import FileStorage
from durus.connection import Connection
from grail2.server import ConnectionFactory
from twisted.internet import reactor
import sys
import logging

logging.basicConfig(level = logging.DEBUG,
                    format = '%(asctime)s %(levelname)s %(message)s',
                    stream = sys.stdout)

def construct_mud(objstorethunk):
    """Construct a MUD factory."""
    return ConnectionFactory(objstorethunk)

def run_mud(mud, port):
    """Run the MUD factory."""
    reactor.listenTCP(port, mud)
    mud.ticker.start()
    reactor.run()

if __name__ == '__main__':
    #this needs to be wrapped in a lambda, because Durus is quite eager to load
    #stuff. If it wasn't so eager, the ConnectionFactory would just pull what
    #it needed when, rather than getting silly errors on the next line.
    connection = lambda: Connection(FileStorage("mudlib.durus"))
    run_mud(construct_mud(connection), 6666)
