from pyparsing import *
from grail2.events import BaseEvent
from grail2.utils import promptcolour
from grail2.objects import TargettableObject, definein
from grail2.actiondefs.system import badSyntax
from string import whitespace
from grail2.strutils import wsnormalise

class LDescSetEvent(BaseEvent):

    def __init__(self, desc):
        self.desc = desc

    @promptcolour("speech")
    def collapseToText(self, state, obj):
        state.sendEventLine("Your long descrption is now:")
        state.sendEventLine(self.desc)

    def __repr__(self):
        return "%s(%r)" % (type(self).__name__, self.desc)

#I don't know how or why this works, but it does.
ldesc_pattern = Suppress("ldesc" + ZeroOrMore(' ')) + restOfLine

syntax_message = "'%r' is an unknown option for the 'set' action."

def setDistribute(actor, text, info):
    try:
        desc, = ldesc_pattern.parseString(text)
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
        #globanls can't be a dict, but locals can
        return eval(name, {}, self.d)

default_long_desc = "%(sdesc)s. Nothing more, nothing less."

@definein(TargettableObject._instance_variable_factories)
def ldesc(self):
    return default_long_desc % SmartDictWrapper(Dictator(self))

def register(cdict):
    cdict['set'] = setDistribute
