from pyparsing import *
from grail2.events import AudibleEvent, GameEvent
from grail2.objects import AgentObject, MUDObject, definein
from grail2.actiondefs.system import badSyntax
from grail2.utils import promptcolour

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

@definein(MUDObject._instance_variable_factories)
def deaf():
    return False

@MUDObject.receiveEvent.register(AgentObject, AudibleEvent)
def receiveEvent(self, event):
    """Ignore sound events for deaf things."""
    if not self.deaf:
        MUDObject.receiveEvent.call_next_method()

def register(cdict):
    cdict['deaf'] = deafDistributor
