from pyparsing import *
from grail2.events import AudibleEvent, GameEvent
from grail2.objects import MUDObject, definein
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

syntaxmessage = "Use 'deaf on' to turn deafness on, or 'deaf off' to turn "\
                "deafness off."

def deafDistributor(actor, rest, lineinfo):
    rest = rest.lower()
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
    badSyntax(actor, syntaxmessage)

def deafOn(actor):
    if not actor.deaf:
        actor.deaf = True
        actor.receiveEvent(DeafnessOnEvent())
    else:
        actor.receiveEvent(DeafnessOnAlreadyEvent())

def deafOff(actor):
    if not actor.deaf:
        actor.receiveEvent(DeafnessOffAlreadyEvent())
    else:
        actor.deaf = False
        actor.receiveEvent(DeafnessOffEvent())

@definein(MUDObject._instance_variable_factories)
def deaf(self):
    return False

@MUDObject.receiveEvent.register(MUDObject, AudibleEvent)
def receiveEvent(self, event):
    """Ignore sound events for deaf things."""
    if not self.deaf:
        MUDObject.receiveEvent.call_next_method()

def register(cdict):
    cdict['deaf'] = deafDistributor
