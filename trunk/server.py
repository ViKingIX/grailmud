"""Handles server initialisation and pulls some Twisted ropes."""

__copyright__ = """Copyright 2007 Sam Pointon"""

__licence__ = """
This file is part of grailmud.

grailmud is free software; you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation; either version 2 of the License, or (at your option) any later
version.

grailmud is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
grailmud (in the file named LICENSE); if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301  USA
"""

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

