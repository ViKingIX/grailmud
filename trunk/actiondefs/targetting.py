from pyparsing import *
from grail2.events import BaseEvent
from grail2.objects import MUDObject
from grail2.utils import monkeypatch, promptcolour
from grail2.rooms import UnfoundError
from grail2.actiondefs.core import object_pattern, shorttarget_pattern, \
                                   get_from_rooms
from grail2.actiondefs.system import permissionDenied, badSyntax, unfoundObject

@monkeypatch(MUDObject)
def __init__(self, *args, **kwargs):
    self.targetting_shorts = {}

class TargetSetEvent(BaseEvent):
    '''A target's been set to a value.'''
    def __init__(self, name, target):
        self.name = name
        self.target = target

    @promptcolour()
    def collapseToText(self, state, obj):
        state.sendEventLine('You may now refer to %s as $%s.'
                            % (self.target.sdesc, self.name))

class TargetClearedEvent(BaseEvent):
    '''An existing target has been cleared.'''
    def __init__(self, name):
        self.name = name

    @promptcolour()
    def collapseToText(self, state, obj):
        state.sendEventLine("Target $%s cleared." % self.name)

class TargetAlreadyClearedEvent(BaseEvent):
    '''A nonexistant target was cleared.'''
    def __init__(self, name):
        self.name = name

    @promptcolour()
    def collapseToText(self, state, obj):
        state.sendEventLine("You have no target $%s." % self.name)

class TargetListEvent(BaseEvent):
    '''The user asked for a list of targets.'''
    def __init__(self, actor):
        self.actor = actor

    @promptcolour()
    def collapseToText(self, state, obj):
        state.sendEventLine("You have set these targets:")
        for name, obj in self.actor.targetting_shorts.itervalues():
            state.sendEventLine("%s: %s" % (name, obj.sdesc))

target_set_pattern = Suppress('set') + shorttarget_pattern + Suppress('to') + \
                     object_pattern

target_clear_pattern = Suppress('clear') + shorttarget_pattern

target_list_pattern = Suppress('list')

def targetDistributor(actor, text, info):
    if info.instigator is not actor:
        permissionDenied(info.instigator)
        return
    try:
        name, blob = target_set_pattern.parseString(text)
    except ParseException:
        pass
    else:
        try:
            target = get_from_rooms(blob, [actor.inventory, actor.room], info)
        except UnfoundError:
            unfoundObject(actor)
        else:
            actor.targetting_shorts[name] = target
        return
    try:
        name = target_clear_pattern.parseString(text)
    except ParseException:
        pass
    else:
        targetClear(actor, name)
        return
    try:
        target_list_pattern.parseString(text)
    except ParseException:
        pass
    else:
        targetList(actor)
        return
    badSyntax(actor)

def targetSet(actor, name, target):
    actor.targetting_shorts[name] = target
    actor.receiveEvent(TargetSetEvent(name, target))

def targetClear(actor, name):
    if name in actor.targetting_shorts:
        del actor.targetting_shorts[name]
        actor.receiveEvent(TargetClearedEvent(name))
    else:
        actor.receiveEvent(TargetAlreadyClearedEvent(name))

def targetList(actor):
    actor.receiveEvent(TargetListEvent(actor))

def register(cdict):
    cdict['target'] = targetDistributor
