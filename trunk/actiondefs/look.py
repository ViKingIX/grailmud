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
from grail2.actiondefs.core import object_pattern, get_from_rooms, \
                                   distributeEvent
from grail2.events import VisibleEvent
from grail2.rooms import UnfoundError
from grail2.actiondefs.system import unfoundObject
from grail2.objects import Player, TargettableObject, ExitObject, MUDObject
from grail2.strutils import capitalise
from grail2.utils import promptcolour
from grail2.multimethod import Multimethod

class LookAtEvent(VisibleEvent):

    def __init__(self, target):
        self.target = target

    @promptcolour()
    def collapseToText(self, state, obj):
        state.sendEventLine(capitalise(self.target.ldesc))

class LookRoomEvent(VisibleEvent):

    def __init__(self, room):
        self.room = room

    @promptcolour("room title")
    def collapseToText(self, state, obj):
        state.sendEventLine(self.room.title)
        state.setColourName("room desc")
        state.sendEventLine(self.room.desc)
        state.setColourName("people list")
        peopleList = ["%s is here." % capitalise(obj.sdesc)
                      for obj in self.room.contents]
        state.sendEventLine(" ".join(peopleList))

lookAtPattern = Suppress(Optional(Keyword("at"))) + \
                object_pattern

def lookDistributor(actor, text, info):
    try:
        blob = lookAtPattern.parseString(text)
    except ParseException:
        lookRoom(actor)
        return
    try:
        target = get_from_rooms(blob, [actor.inventory, actor.room], info)
    except UnfoundError:
        pass
    else:
        lookAt(actor, target)
    unfoundObject(actor)

lookAt = Multimethod()

@lookAt.register(MUDObject, MUDObject)
def lookAt(actor, target):
    unfoundObject(actor)

@lookAt.register(MUDObject, TargettableObject)
def lookAt(actor, target):
    if target.room not in [actor.inventory, actor.room]:
        unfoundObject(actor)
    else:
        actor.receiveEvent(LookAtEvent(target))

@lookAt.register(MUDObject, ExitObject)
def lookAt(actor, target):
    if target.room is not actor.room: #stricter deliberately.
        print 'Not in room'
        unfoundObject(actor)
    else:
        print 'Sending event...'
        actor.receiveEvent(LookRoomEvent(target.target_room))

def lookRoom(actor):
    actor.receiveEvent(LookRoomEvent(actor.room))

def register(cdict):
    cdict['l'] = lookDistributor
    cdict['look'] = lookDistributor
