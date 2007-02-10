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

from pyparsing import *
from grail2.events import BaseEvent
from grail2.utils import promptcolour

class WhoHereEvent(BaseEvent):

    def __init__(self, objects):
        self.objects = objects

    @promptcolour("speech")
    def collapseToText(self, state, obj):
        state.sendEventLine("You see the following things present:")
        state.setColourName("people list")
        state.sendEventLine(', '.join(obj.sdesc for obj in self.objects))

class WhoEvent(BaseEvent):

    @promptcolour("speech")
    def collapseToText(self, state, obj):
        state.sendEventLine("No 'who' functionality yet.")

whoHerePattern = Suppress("here")

def whoDistributor(actor, text, info):
    try:
        whoHerePattern.parseString(text)
    except ParseException:
        who(actor)
    else:
        whoHere(actor)

def whoHere(actor):
    actor.receiveEvent(WhoHereEvent(actor.room.contents))

def who(actor):
    actor.receiveEvent(WhoEvent(actor))

def register(cdict):
    cdict['who'] = whoDistributor
    cdict['wh'] = cdict['whohere'] = lambda actor, text, info: whoHere(actor)
