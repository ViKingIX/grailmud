"""Emotes/ At present, only user-customised, but eventually I'll get round to
writing some prefab ones.
"""
from pyparsing import *
from string import printable
from grail2.events import GameEvent
from grail2.rooms import UnfoundError
from grail2.utils import promptcolour, smartdict, in_rooms
from grail2.strutils import wsnormalise
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
    if target.room not in [actor.room, actor.inventory]:
        unfoundObject()
        return
    first = process(first)
    second = process(second)
    third = process(third)
    actor.receiveEvent(EmoteTargettedFirst(target, first))
    target.receiveEvent(EmoteTargettedSecond(actor, second))
    distributeEvent(actor.room, [actor, target],
                    EmoteTargettedThird(actor, target, third))

class YankedUntargetted(object):

    def __init__(self, first, third = None):
        self.first = first
        self.third = third

    def __call__(self, actor, text, info):
        self.send_out_events(actor)

    def send_out_events(self, actor):
        if self.third is not None:
            emote(actor, self.first, self.third)
        else:
            #solipsism
            actor.receiveEvent(EmoteUntargettedFirst(actor, self.first))

class YankedTargetted(object):
    
    def __init__(self, first, second, third, fallback):
        self.first = first
        self.second = second
        self.third = third

    def __call__(self, actor, text, info):
        try:
            blob, = object_pattern.parseString(text)
        except ParseException:
            self.fallback(actor)
        else:
            target = get_from_rooms(blob, [actor.inventory, actor.room], info)
            self.send_out_events(actor, target)

    def send_out_events(self, actor, target):
        emoteTo(actor, target, self.first, self.second, self.third)

def yank_emotes(cdict, emotefile):
    emote_definitions = get_dict_definitions(emotefile)
    for definition in emote_definitions:
        if 'untargetted' in definition:
            function = untargetted = \
                                 YankedUntargetted(**definition['untargetted'])
        else:
            untargetted = unfoundObject()
        if 'targetted' in definition:
            function = YankedTargetted(fallback = untargetted,
                                       **definition['targetted'])
        for name in definition['names']:
            cdict[name] = function

def register(cdict):
    cdict['emote'] = emoteWrapper
    cdict['emoteto'] = emoteToWrapper
    cdict['emote,'] = emoteToWrapper
    
def process(text):
    text = wsnormalise(text)
    text = text.replace(' ~', ' %(actor.sdesc)s')
    text = text.replace(' @', ' %(target.sdesc)s')
    return text
