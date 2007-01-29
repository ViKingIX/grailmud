from string import ascii_letters, digits
from grail2.multimethod import Multimethod
from pyparsing import *
from grail2.rooms import UnfoundError
from grail2.events import SystemEvent
import logging

#Some utilities.
shorttarget_pattern = Suppress('$') + Group(Word(ascii_letters + digits))
adjs_pattern = Group(OneOrMore(Word(ascii_letters))) + Optional(Word(digits))

object_pattern = Or(adjs_pattern, shorttarget_pattern)

def distributeEvent(room, nodis, event):
    logging.debug('Distributing event %s' % event)
    for obj in room.contents:
        if obj not in nodis:
            obj.receiveEvent(event)

def adjs_num_parse((adjs, number), info):
    adjs = frozenset(x.lower() for x in adjs)
    number = int(number) if number else 0
    return adjs, number

def get_from_rooms(blob, rooms, info):
    if len(blob) == 2:
        adjs, num = adjs_num_parse(blob)
        for room in rooms:
            return room.matchContent(adjs, num)
        raise UnfoundError
    elif len(blob) == 1:
        try:
            obj = info.instigator.targetting_shorts[blob[0]]
        except KeyError:
            raise UnfoundError
        for room in rooms:
            if obj in room:
                return obj
        raise UnfoundError
    raise RuntimeError("Shouldn't get here.")

class UnfoundActionEvent(SystemEvent):

    def collapseToText(self, state, obj):
        state.forcePrompt()
        state.setColourName('normal')
        state.sendEventLine("I don't understand. Syntax error?")

def unfoundAction(actor, text, info):
    actor.receiveEvent(UnfoundActionEvent())

def register(cdict):
    cdict.default_factory = lambda: unfoundAction
