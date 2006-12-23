from pyparsing import *
from grail2.actiondefs.core import BaseEvent

class WhoHereEvent(BaseEvent):

    def __init__(self, objects):
        self.objects = objects

    def collapseToText(self, state, obj):
        state.forcePrompt()
        state.setColourName("normal")
        state.sendEventLine("You see the following things present:")
        state.setColourName("people list")
        state.sendEventLine(', '.join(obj.sdesc for obj in self.objects))

class WhoEvent(BaseEvent):

    def collapseToText(self, state, obj):
        state.forcePrompt()
        state.setColourName("normal")
        state.sendEventLine("No 'who' functionality yet.")

whoHerePattern = Suppress("here")

def whoDistributor(actor, text, info):
    try:
        whoHerePattern.parseString(text)
    except ParseException:
        who(actor)
    else:
        whoHere(actor)

def whoHere(actor):
    actor.receiveEvent(WhoHereEvent(actor.room.contents))

def who(actor):
    actor.receiveEvent(WhoEvent(actor))

def register(cdict):
    cdict['who'] = whoDistributor
    cdict['wh'] = cdict['whohere'] = lambda actor, text, info: whoHere(actor)
