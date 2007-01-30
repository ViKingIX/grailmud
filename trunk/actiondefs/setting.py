from pyparsing import *
from grail2.events import BaseEvent
from grail2.utils import promptcolour
from grail2.objects import TargettableObject, definein
from grail2.actiondefs.system import badSyntax

class LDescSetEvent(BaseEvent):

    def __init__(self, desc):
        self.desc = desc

    @promptcolour("speech")
    def collapseToText(self, state, obj):
        state.sendEventLine("Your long descrption is now:")
        state.sendEventLine(self.desc)

ldesc_pattern = Suppress("ldesc") + Word(printables)

syntax_message = "'%r' is an unknown option for the 'set' action."

def setDistribute(actor, text, info):
    try:
        desc = ldesc_pattern.parseString(text)
    except ParseException:
        badSyntax(actor, syntax_message % text)
    else:
        setLDesc(actor, desc)

def setLDesc(actor, desc):
    actor.ldesc = desc
    actor.receiveEvent(LDescSetEvent(desc))

class Dictator(object):

    def __init__(self, obj):
        self.obj = obj

    def __getitem__(self, name):
        if hasattr(self.obj, name):
            return getattr(self.obj, name)
        raise KeyError

class SmartDictWrapper(object):

    def __init__(self, d):
        self.d = d

    def __getitem__(self, name):
        return eval(name, d)

default_long_desc = "%(sdesc)s. Nothing more, nothing less."

@definein(TargettableObject._instance_variable_factories)
def ldesc(self):
    return default_long_desc % SmartDictWrapper(Dictator(self))

def register(cdict):
    cdict['set'] = setDistribute
