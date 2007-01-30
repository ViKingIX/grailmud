import logging
from grail2.actiondefs.core import distributeEvent
from grail2.strutils import capitalise
from grail2.events import SystemEvent, GaneEvent
from grail2.utils import promptcolour

class UnfoundObjectEvent(GameEvent):

    @promptcolour()
    def collapseToText(self, state, obj):
        state.sendEventLine("That object is not present.")

class BlankLineEvent(SystemEvent):

    def collapseToText(self, state, obj):
        state.forcePrompt()
        state.sendEventLine('')

class PermissionDeniedEvent(SystemEvent):

    @promptcolour("system")
    def collapseToText(self, state, obj):
        state.sendEventLine("Hey, you can't do that!")

class BadSyntaxEvent(SystemEvent):

    def __init__(self, expl):
        self.expl = expl

    @promptcolour("system")
    def collapseToText(self, state, obj):
        expl = "Couldn't parse that, I'm afraid."
        if self.expl is not None:
            expl = " ".join([expl, self.expl])
        state.sendEventLine(expl)

def blankLine(actor, text, info):
    actor.receiveEvent(BlankLineEvent())

def permissionDenied(actor):
    actor.receiveEvent(PermissionDeniedEvent())

def badSyntax(actor, expl = None):
    actor.receiveEvent(BadSyntaxEvent(expl))

def unfoundObject(actor):
    actor.receiveEvent(UnfoundObjectEvent())

def register(cdict):
    cdict[''] = blankLine
