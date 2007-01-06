# pylint: disable-msg=C0103,W0613,W0231,R0903
#pylint and its finickity names and insistence that every single argument be
#used somewhere and that every single __init__ next-method is called and that
#classes need at least 2 methods...
import logging
from grail2.actiondefs.core import distributeEvent
from grail2.strutils import capitalise
from grail2.events import SystemEvent
from grail2.utils import promptcolour
from grail2.objects import Player

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

class UnfoundObjectEvent(SystemEvent):

    @promptcolour()
    def collapseToText(self, state, obj):
        state.sendEventLine("That object is not present.")

class BlankLineEvent(SystemEvent):

    def collapseToText(self, state, obj):
        state.forcePrompt()
        state.sendEventLine('')

class PermissionDeniedEvent(SystemEvent):

    @promptcolour()
    def collapseToText(self, state, obj):
        state.sendEventLine("Hey, you can't do that!")

class BadSyntaxEvent(SystemEvent):

    def __init__(self, expl):
        self.expl = expl

    @promptcolour()
    def collapseToText(self, state, obj):
        expl = "Couldn't parse that, I'm afraid."
        if self.expl is not None:
            expl = " ".join([expl, self.expl])
        state.sendEventLine(expl)

def blankLine(actor, text, info):
    actor.receiveEvent(BlankLineEvent())

def quitGame(actor, text, info):
    if info.instigator is not actor:
        info.instigator.receiveEvent(PermissionDeniedEvent())
    else:
        logoffFinal(actor)

def login(actor):
    '''Perform some initialisation for the Player being logged in.'''
    assert isinstance(actor, Player)
    actor.connstate = 'online'
    actor.session = {}
    actor.receiveEvent(LoginFirstEvent())
    distributeEvent(actor.room, [actor], LoginThirdEvent(actor))

def logoffFinal(actor):
    assert isinstance(actor, Player)
    if actor.connstate != 'online':
        logging.info("Foiled a double logoff attempt with %r." % actor)
        return
    actor.connstate = 'offline'
    actor.receiveEvent(LogoffFirstEvent())
    distributeEvent(actor.room, [actor], LogoffThirdEvent(actor))
    actor.disconnect()
    actor.room.remove(actor)

def permissionDenied(actor):
    actor.receiveEvent(PermissionDeniedEvent())

def badSyntax(actor, expl = None):
    actor.receiveEvent(BadSyntaxEvent(expl))

def unfoundObject(actor):
    actor.receiveEvent(UnfoundObjectEvent())

def register(cdict):
    cdict[''] = blankLine
    cdict['qq'] = quitGame
    cdict['quit'] = quitGame
