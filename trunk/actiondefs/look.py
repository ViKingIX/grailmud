# pylint: disable-msg=W0611,E0102
#we import the whole of pyparsing for convenience's sake.
#we also redefine multimethods using the same name for emphasis and a lack of
#namespace pollution.
from pyparsing import *
from grail2.actiondefs.core import object_pattern, get_from_rooms, \
                                   UnfoundMethod, distributeEvent
from grail2.events import VisibleEvent
from grail2.actiondefs.system import unfoundObject
from grail2.rooms import UnfoundError
from grail2.objects import Player, TargettableObject, ExitObject, MUDObject
from grail2.strutils import capitalise
from grail2.utils import promptcolour

class LookAtEvent(VisibleEvent):

    def __init__(self, target):
        self.target = target

    @promptcolour()
    def collapseToText(self, state, obj):
        desc = getattr(self.target, 'ldesc',
                       "They're %s. Nothing more, nothing less."
                       % self.target.sdesc)
        state.sendEventLine(capitalise(desc))

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

def look(actor, text, info):
    try:
        blob = lookAtPattern.parseString(text)
    except ParseException:
        lookRoom(actor)
        return
    try:
        target = get_from_rooms(blob, [actor.inventory, actor.room], info)
    except UnfoundError:
        unfoundObject(actor)
    else:
        lookAt(actor, target)

lookAt = UnfoundMethod()

@lookAt.register(MUDObject, TargettableObject)
def lookAt(actor, target):
    if target not in actor.room and target not in actor.inventory:
        unfoundObject(actor)
    else:
        actor.receiveEvent(LookAtEvent(target))

@lookAt.register(MUDObject, ExitObject)
def lookAt(actor, target):
    if target not in actor.room: #stricter deliberately.
        unfoundObject(actor)
    else:
        actor.receiveEvent(LookRoomEvent(target.target_room))

def lookRoom(actor):
    actor.receiveEvent(LookRoomEvent(actor.room))

def register(cdict):
    cdict['l'] = look
    cdict['look'] = look
