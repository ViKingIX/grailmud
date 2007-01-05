# pylint: disable-msg=W0611
#we import the whole of pyparsing for convenience's sake.
from pyparsing import *
from grail2.events import BaseEvent
from grail2.utils import promptcolour

class UnknownOptionEvent(BaseEvent):

    def __init__(self, command):
        self.command = command

    @promptcolour("speech")
    def collapseToText(self, state, obj):
        state.sendEventLine("That is an unknown option with the '%s' command."
                            % self.command)

class LDescSetEvent(BaseEvent):

    def __init__(self, desc):
        self.desc = desc

    @promptcolour("speech")
    def collapseToText(self, state, obj):
        state.sendEventLine("Your long descrption is now:")
        state.sendEventLine(self.desc)

ldesc_pattern = Suppress("ldesc") + Word(printables)

def setDistribute(actor, text, info):
    try:
        desc = ldesc_pattern.parseString(text)
    except ParseException:
        unknownOption(actor, "set")
    else:
        setLDesc(actor, desc)

def unknownOption(actor, command):
    actor.receiveEvent(UnknownOptionEvent(command))

def setLDesc(actor, desc):
    actor.ldesc = desc
    actor.receiveEvent(LDescSetEvent(desc))

def register(cdict):
    cdict['set'] = setDistribute
