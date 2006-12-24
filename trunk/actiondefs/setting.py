# pylint: disable-msg=W0611
#we import the whole of pyparsing for convenience's sake.
from pyparsing import *
from grail2.actiondefs.core import BaseEvent, object_pattern, adjs_num_parse,\
                                   distributeEvent

class UnknownOptionEvent(BaseEvent):

    def __init__(self, command):
        self.command = command

    def collapseToText(self, state, obj):
        state.forcePrompt()
        state.setColourName("normal")
        state.sendEventLine("That is an unknown option with the '%s' command."
                            % self.command)

class LDescSetEvent(BaseEvent):

    def __init__(self, desc):
        self.desc = desc

    def collapseToText(self, state, obj):
        state.forcePrompt()
        state.setColourName("normal")
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
    actor.receiveEvent(LDescSetEvent(levent))

def register(cdict):
    cdict['set'] = setDistributor
