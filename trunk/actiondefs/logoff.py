import logging
from grail2.events import SystemEvent
from grail2.utils import promptcolour
from grail2.strutils import capitalise

class LogoffFirstEvent(SystemEvent):

    @promptcolour()
    def collapseToText(self, state, obj):
        state.sendEventLine("Goodbye!")
        state.dontWantPrompt()

class LogoffThirdEvent(SystemEvent):

    def __init__(self, actor):
        self.actor = actor

    @promptcolour()
    def collapseToText(self, state, obj):
        state.sendEventLine("%s has left the game." %
                            capitalise(self.actor.sdesc))


def quitGame(actor, text, info):
    if info.instigator is not actor:
        info.instigator.receiveEvent(PermissionDeniedEvent())
    else:
        logoffFinal(actor)

def logoffFinal(actor):
    #XXX: is this doing stuff in the correct order?
    if actor.connstate != 'online':
        logging.info("Foiled a double logoff attempt with %r." % actor)
        return
    actor.connstate = 'offline'
    actor.receiveEvent(LogoffFirstEvent())
    distributeEvent(actor.room, [actor], LogoffThirdEvent(actor))
    actor.disconnect()
    actor.room.remove(actor)

def register(cdict):
    cdict['qq'] = quitGame
    cdict['quit'] = quitGame
