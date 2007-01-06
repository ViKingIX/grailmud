# pylint: disable-msg=C0103,W0613,W0231,R0903,W0611
#pylint and its finickity names and insistence that every single argument be
#used somewhere and that every single __init__ next-method is called and that
#classes need at least 2 methods...
#oh, and we import the whole of pyparsing for convenience's sake.
from pyparsing import *
from grail2.events import AudibleEvent, GameEvent
from grail2.objects import MUDObject
from grail2.actiondefs.system import badSyntax
from grail2.utils import monkeypatch, promptcolour

class DeafnessOnEvent(GameEvent):

    @promptcolour()
    def collapseToText(self, state, obj):
        state.sendEventLine("You forcibly shut out all sound, making the world"
                            "silent. Aah. Silence is golden.")

class DeafnessOnAlreadyEvent(GameEvent):

    @promptcolour()
    def collapseToText(self, state, obj):
        state.sendEventLine("You're already deaf, silly!")

class DeafnessOffEvent(GameEvent):

    @promptcolour()
    def collapseToText(self, state, obj):
        state.sendEventLine("You once again begin to hear sounds from the "
                            "world around you.")
            

class DeafnessOffAlreadyEvent(GameEvent):

    @promptcolour()
    def collapseToText(self, state, obj):
        state.sendEventLine("You're not deaf, silly!")

on_pattern = Literal('on')
off_pattern = Literal('off')

def deafDistributor(actor, rest, lineinfo):
    try:
        on_pattern.parseString(rest)
    except ParseException:
        pass
    else:
        deafOn(actor)
        return
    try:
        off_pattern.parseString(rest)
    except ParseException:
        pass
    else:
        deafOff(actor)
        return
    badSyntax(actor, "Use 'deaf on' to turn deafness on, or 'deaf off' to turn "
                     "deafness off.")

def deafOn(actor):
    if actor.deaf:
        actor.deaf = True
        actor.receiveEvent(DeafnessOnEvent())
    else:
        actor.receiveEvent(DeafnessOnAlreadyEvent())

def deafOff(actor):
    if actor.deaf:
        actor.receiveEvent(DeafnessOffAlreadyEvent())
    else:
        actor.deaf = False
        actor.receiveEvent(DeafnessOffEvent())

@monkeypatch(MUDObject)
def __init__(self, *args, **kwargs):
    self.deaf = False

@MUDObject.receiveEvent.register(MUDObject, AudibleEvent)
def receiveEvent(self, event):
    """Ignore sound events for deaf things."""
    if not self.deaf:
        MUDObject.receiveEvent.call_next_method()

def register(cdict):
    cdict['deaf'] = deafDistributor
