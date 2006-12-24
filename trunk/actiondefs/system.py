import logging
from grail2.actiondefs.core import BaseEvent, distributeEvent
from grail2.strutils import capitalise

class LogoffFirstEvent(BaseEvent):

    def collapseToText(self, state, obj):
        state.forcePrompt()
        state.setColourName('normal')
        state.sendEventLine("Goodbye!")
        state.dontWantPrompt()

class LogoffThirdEvent(BaseEvent):

    def __init__(self, actor):
        self.actor = actor

    def collapseToText(self, state, obj):
        state.forcePrompt()
        state.setColourName('normal')
        state.sendEventLine("%s has left the game." %
                            capitalise(self.actor.sdesc))

class LoginThirdEvent(BaseEvent):

    def __init__(self, actor):
        self.actor = actor

    def collapseToText(self, state, obj):
        state.forcePrompt()
        state.setColourName("normal")
        state.sendEventLine("%s's form appears, and they crackle into life." %
                            capitalise(self.actor.dsesc))

class LoginFirstEvent(BaseEvent):

    def collapseToText(self, state, obj):
        state.setColourName('normal')
        state.sendEventLine("Welcome to the game.")

class UnfoundObjectEvent(BaseEvent):

    def collapseToText(self, state, obj):
        state.forcePrompt()
        state.setColourName("normal")
        state.sendEventLine("That object is not present.")

class BlankLineEvent(BaseEvent):

    def collapseToText(self, state, obj):
        state.forcePrompt()
        state.sendEventLine('')

class PermissionDeniedEvent(BaseEvent):

    def collapseToText(self, state, obj):
        state.forcePrompt()
        state.setColourName('normal')
        state.sendEventLine("Hey, you can't do that!")

class BadSyntaxEvent(BaseEvent):

    def __init__(self, expl):
        self.expl = expl

    def collapseToText(self, state, obj):
        state.forcePrompt()
        state.setColourName("normal")
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
    actor.receiveEvent(LoginFirstEvent())
    distributeEvent(actor.room, [actor], LoginThirdEvent(actor))

def logoffFinal(actor):
    if getattr(actor, 'logged_off', False):
        logging.info("Foiled a double logoff attempt with %r." % actor)
        return
    actor.logged_off = True
    actor.receiveEvent(LogoffFirstEvent())
    distributeEvent(actor.room, [actor], LogoffThirdEvent(actor))
    for listener in actor.listeners.copy(): #copy because we mutate it
        actor.removeListener(listener)
    actor.room.remove(actor)

def badSyntax(actor, expl = None):
    actor.receiveEvent(BadSyntaxEvent(expl))

def unfoundObject(actor):
    actor.receiveEvent(UnfoundObjectEvent())

def register(cdict):
    cdict[''] = blankLine
    cdict['qq'] = quitGame
    cdict['quit'] = quitGame
