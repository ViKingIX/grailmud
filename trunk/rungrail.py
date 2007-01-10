# pylint: disable-msg=E1101
#twisted does some hackery with the reactor that pylint doesn't know about.
"""This module is intended to be the main entry point for the server, run from
the shell.
"""
from durus.file_storage import FileStorage
from durus.connection import Connection
import grail2
from grail2.server import ConnectionFactory
from twisted.internet import reactor
import sys
import logging

logging.basicConfig(level = logging.DEBUG,
                    format = '%(asctime)s %(levelname)s %(message)s',
                    stream = sys.stdout)

def construct_mud(tickfreq, objstore):
    """Construct a MUD factory."""
    return ConnectionFactory(tickfreq, objstore, objstore.get_root().startroom)

def run_mud(mud, port):
    """Run the MUD factory."""
    reactor.listenTCP(port, mud)
    grail2.instance = mud
    reactor.run()

if __name__ == '__main__':
    connection = Connection(FileStorage("mudlib.durus"))
    run_mud(construct_mud(100, connection), 6666)
