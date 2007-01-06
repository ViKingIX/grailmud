# pylint: disable-msg=C0103,W0613,W0231,R0903,W0611
#pylint and its finickity names and insistence that every single argument be
#used somewhere and that every single __init__ next-method is called and that
#classes need at least 2 methods...
#oh, and we import the whole of pyparsing for convenience's sake.
"""Emotes/ At present, only user-customised, but eventually I'll get round to
writing some prefab ones.
"""
from pyparsing import *
from string import printable
from grail2.events import GameEvent
from grail2.rooms import UnfoundError
from grail2.utils import promptcolour, smartdict, in_rooms
from grail2.actiondefs.core import object_pattern, get_from_rooms, \
                                   distributeEvent
from grail2.actiondefs.system import badSyntax, unfoundObject

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

class EmoteTargettedSecond(GameEvent):

    def __init__(self, actor, message):
        self.actor = actor
        self.message = message

    @promptcolour('emote')
    def collapseToText(self, state, obj):
        state.sendEventLine(self.message % smartdict({'actor': self.actor}))

class EmoteTargettedThird(GameEvent):

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
    emoteTo(actor, target, 'You have emoted: ' + text, text, text)

def emote(actor, first, third):
    first = process(first)
    third = process(third)
    actor.receiveEvent(EmoteUntargettedFirst(actor, first))
    distributeEvent(actor.room, [actor],
                    EmoteUntargettedThird(actor, third))

def emoteTo(actor, target, first, second, third):
    if not in_rooms(target, [actor.room, actor.inventory]):
        unfoundObject()
        return
    first = process(first)
    second = process(second)
    third = process(third)
    actor.receiveEvent(EmoteTargettedFirst(target, first))
    target.receiveEvent(EmoteTargettedSecond(actor, second))
    distributeEvent(actor.room, [actor, target],
                    EmoteTargettedThird(actor, target, third))

def lookUpDistributor(actor, text, info):
    try:
        blob, = object_pattern.parseString(text)
    except ParseException:
        lookUp(actor)
    else:
        target = get_from_rooms(blob, [actor.inventory, actor.room], info)
        lookUpAt(actor, target)

def lookUp(actor):
    emote(actor, 'You look up expectantly.', '~ looks up expectantly.')

def lookUpAt(actor, target):
    emoteTo(actor, target, 'You look up at @ expectantly.',
            '~ looks up at you expectantly.', '~ looks up at @ expectantly.')

def register(cdict):
    cdict['emote'] = emoteWrapper
    cdict['emoteto'] = emoteToWrapper
    cdict['emote,'] = emoteToWrapper
    
def process(text):
    text = text.replace('~', '%(actor.sdesc)s')
    text = text.replace('@', '%(target.sdesc)s')
    return text
