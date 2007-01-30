import logging
from grail2.actiondefs.core import distributeEvent
from grail2.strutils import capitalise
from grail2.events import SystemEvent
from grail2.utils import promptcolour

class LoginThirdEvent(SystemEvent):

    def __init__(self, actor):
        self.actor = actor

    @promptcolour()
    def collapseToText(self, state, obj):
        state.sendEventLine("%s's form appears, and they crackle into life." %
                            capitalise(self.actor.dsesc))

class LoginFirstEvent(SystemEvent):

    def collapseToText(self, state, obj):
        state.setColourName('normal')
        state.sendEventLine("Welcome to the game.")

def login(actor):
    '''Perform some initialisation for the Player being logged in.'''
    actor.connstate = 'online'
    actor.chunked_event = None
    actor.chunks = iter([])
    actor.receiveEvent(LoginFirstEvent())
    distributeEvent(actor.room, [actor], LoginThirdEvent(actor))
