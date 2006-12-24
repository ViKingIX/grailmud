# pylint: disable-msg=W0611
#we import the whole of pyparsing for convenience's sake.
from pyparsing import *
from grail2.actiondefs.core import BaseEvent, object_pattern, adjs_num_parse,\
                                   UnfoundMethod, distributeEvent
from grail2.actiondefs.system import unfoundObject
from grail2.rooms import UnfoundError
from grail2.objects import Player, TargettableObject, ExitObject, MUDObject
from grail2.strutils import capitalise

class LookAtEvent(BaseEvent):

    def __init__(self, target):
        self.target = target

    def collapseToText(self, state, obj):
        state.forcePrompt()
        state.setColourName('normal')
        desc = getattr(self.target, 'ldesc',
                       "They're %s. Nothing more, nothing less."
                       % self.target.sdesc)
        state.sendEventLine(capitalise(desc))

class LookRoomEvent(BaseEvent):

    def __init__(self, room):
        self.room = room

    def collapseToText(self, state, obj):
        state.forcePrompt()
        state.setColourName("room title")
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
        raw_an = lookAtPattern.parseString(text)
    except ParseException:
        lookRoom(actor)
        return
    adjs, number = adjs_num_parse(raw_an)
    try:
        target = actor.room.matchContent(adjs, number)
        lookAt(actor, target)
    except UnfoundError:
        unfoundObject(actor)

lookAt = UnfoundMethod()

@lookAt.register(MUDObject, TargettableObject)
def lookAt(actor, target):
    if target not in actor.room and target not in actor.inventory:
        raise UnfoundError
    else:
        actor.receiveEvent(LookAtEvent(target))

@lookAt.register(MUDObject, ExitObject)
def lookAt(actor, target):
    if target not in actor.room: #stricter deliberately.
        raise UnfoundError
    else:
        actor.receiveEvent(LookRoomEvent(target.target_room))

def lookRoom(actor):
    actor.receiveEvent(LookRoomEvent(actor.room))

def register(cdict):
    cdict['l'] = look
    cdict['look'] = look
