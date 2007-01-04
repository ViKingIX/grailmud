# pylint: disable-msg=W0611
#we import the whole of pyparsing for convenience's sake.
from string import ascii_letters, digits
from grail2.multimethod import Multimethod
from pyparsing import *
from grail2.rooms import UnfoundError
from grail2.events import SystemEvent

#Some utilities.
object_pattern = Group(OneOrMore(Word(ascii_letters))) + Optional(Word(digits))

def distributeEvent(room, nodis, event):
    for obj in room.contents:
        if obj not in nodis:
            obj.receiveEvent(event)

def adjs_num_parse((adjs, number)):
    adjs = frozenset(x.lower() for x in adjs)
    number = int(number) if number else 0
    return adjs, number

class UnfoundMethod(Multimethod):

    def _fail(self):
        raise UnfoundError("Wrong object class.")

class UnfoundActionEvent(SystemEvent):

    def collapseToText(self, state, obj):
        state.forcePrompt()
        state.setColourName('normal')
        state.sendEventLine("I don't understand. Syntax error?")

def unfoundAction(actor, text, info):
    actor.receiveEvent(UnfoundActionEvent())

def register(cdict):
    cdict.default_factory = lambda: unfoundAction
