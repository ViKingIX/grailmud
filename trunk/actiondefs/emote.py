from pyparsing import *
from string import printable
from grail2.events import GameEvent
from grail2.utils import promptcolour, smartdict
from grail2.actiondefs.core import object_pattern, get_from_rooms, \
                                   distributeEvent

class EmoteUntargettedFirst(GameEvent):

    def __init__(self, actor, message):
        self.actor = actor
        self.message = message

    @promptcolour('emote')
    def collapseToText(self, state, obj):
        state.sendEventLine(self.message
                            % smartdict({'actor': self.actor}))

class EmoteUntargettedThird(GameEvent):

    def __init__(self, actor, message):
        self.actor = actor
        self.message = message

    @promptcolour('emote')
    def collapseToText(self, state, obj):
        state.sendEventLine(self.message % smartdict({'actor': self.actor}))

class EmoteTargettedFirst(GameEvent):

    def __init__(self, actor, target, message):
        self.actor = actor
        self.target = target
        self.message = message

    @promptcolour('emote')
    def collapseToText(self, state, obj):
        state.sendEventLine(self.message %
                            smartdict({'target': self.target,
                                       'actor': self.actor}))

class EmoteTagettedSecond(GameEvent):

    def __init__(self, actor, message):
        self.actor = actor
        self.message = message

    @promptcolour('emote')
    def collapseToText(self, state, obj):
        state.sendEventLine(self.message % smartdict({'actor': self.actor}))

class EmoteTagettedThird(GameEvent):

    def __init__(self, actor, target, message):
        self.actor = actor
        self.target = target
        self.message = message

    @promptcolour('emote')
    def collapseToText(self, state, obj):
        state.sendEventLine(self.message % smartdict({'actor': self.actor,
                                                      'target': self.target}))

def emoteWrapper(actor, text, info):
    text = text.replace('%', '%%')
    text = text.replace('$', '%(actor.sdesc)s')
    emote(actor, 'You have emoted: ' + text, text)

emote_to_pattern = object_pattern + Suppress(',') + Word(printable)

def emoteToWrapper(actor, text, info):
    try:
        blob, text = emote_to_pattern.parseString(text)
    except ParseException:
        badSyntax()
        return
    try:
        target = get_from_rooms(blob, [actor.inventory, actor.room], info)
    except UnfoundError:
        unfoundObject()
        return
    text = text.replace('%', '%%')
    text = text.replace('$', '%(actor.sdesc)s')
    text = text.replace('@', '%(target.sdesc)s')
    emoteTo(actor, target, 'You have emoted: ' + text, text, text)

def emote(actor, first, third):
    actor.receiveEvent(EmoteUntargettedFirst(actor, first))
    distributeEvent(actor.room, [actor],
                    EmoteUntargettedThird(actor, third))

def emoteTo(actor, target, first, second, third):
    actor.receiveEvent(EmoteTargettedFirst(target, first))
    target.receiveEvent(EmoteTargettedSecond(actor, second))
    distributeEvent(actor.room, [actor, target],
                    EmoteTargettedThird(actor, target, third))

def register(cdict):
    cdict['emote'] = emoteWrapper
    cdict['emoteto'] = emoteToWrapper
    cdict['emote,'] = emoteToWrapper
    
