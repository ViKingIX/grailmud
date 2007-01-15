"""This file contains an implementation of objects in the MUD and a simple
interface for hooking them up with listeners and events.
"""
import logging
from grail2.strutils import head_word_split
from grail2.rooms import Room
from grail2.multimethod import Multimethod
from grail2.events import BaseEvent
from grail2.utils import InstanceTracker

#XXX: AgentObject and TargetObject are the wrong way around in the class
#hierarchy.
#TODO: some sort of way to tell the classes not to pickle certain attributes.

def definein(dictionary):
    def functiongetter(func):
        dictionary[func.__name__] = func
        return func
    return functiongetter

class MUDObject(InstanceTracker):
    """An object in the MUD."""

    _instance_variable_factories = {}
    
    def __init__(self, room):
        self.room = room

    receiveEvent = Multimethod()

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return self is other

    def __getstate__(self):
        return self.__dict__.copy()

    def __getattr__(self, attr):
        try:
            return InstanceTracker.__getattr__(self, attr)
        except AttributeError:
            for cls in type(self).__mro__:
                if attr in getattr(cls, '_instance_variable_factories', {}):
                    res = cls._instance_variabe_factories[attr]
                    setattr(self, attr, res)
                    return res

@MUDObject.receiveEvent.register(MUDObject, BaseEvent)
def receiveEvent(self, event):
    '''MUDObjects live their merry lives in peace by deafult, ignoring the world
    and its hustle-bustle around them. Kind of cute.
    '''
    pass

class AgentObject(MUDObject):
    """An object that does stuff and has useful stuff done to it."""

    _instance_variable_factories = {}
    
    def __init__(self, room):
        MUDObject.__init__(self, room)
        self.listeners = set()
    
    def eventFlush(self):
        """Tell the listeners that the current lot of events are done."""
        for listener in self.listeners:
            listener.eventListenFlush(self)

    def addListener(self, listener):
        """Register a new listener."""
        listener.register(self)
        self.listeners.add(listener)

    def removeListener(self, listener):
        """Remove a listener. Throws errors if it's not currently listening."""
        listener.unregister(self)
        self.listeners.remove(listener)

    def transferControl(self, obj):
        """Utility method to shift all the listeners to another object."""
        for listener in self.listeners:
            listener.transferControl(self, obj)

    def disconnect(self):
        '''Notify the listeners that this object is being disconnected.

        Note that this only makes sense for Players, but it needs to be on
        here else AttributeErrors will start flying around. I think. So we
        just ignore it.
        '''
        pass

    def __getstate__(self):
        listeners = set(listener for listener in self.listeners
                        if listener._pickleme)
        state = MUDObject.__getstate__(self)
        state['listeners'] = listeners
        return state

@MUDObject.receiveEvent.register(AgentObject, BaseEvent)
def receiveEvent(self, event):
    """Receive an event in the MUD.

    This is the very basic handler for objects that can be listened to.
    """
    for listener in self.listeners:
        listener.listenToEvent(self, event)

class TargettableObject(AgentObject):
    """A tangible object, that can be generically targetted."""

    _name_registry = {}
    _instance_variable_factories = {}
    
    def __init__(self, sdesc, name, adjs, room):
        self.sdesc = sdesc
        self.name = name
        #XXX: this probably ought to be a weakref
        TargettableObject._name_registry[name] = self
        self.adjs = adjs | set([name])
        AgentObject.__init__(self, room)
    
    def match(self, attrs):
        """Check to see if a set of attributes is applicable for this object.
        """
        return (len(attrs) == 1 and self.name in attrs) or \
               self.adjs.issuperset(attrs)

    @classmethod
    def exists(cls, name):
        '''Returns True if an object referred to by a given name exists.'''
        try:
            avatar = TargettableObject._name_registry[name]
        except KeyError:
            return False
        else:
            return isinstance(avatar, cls)

class Player(TargettableObject):
    """A player avatar."""

    _instance_variable_factories = {}

    def __init__(self, name, sdesc, adjs, cmdict, room, passhash):
        self.connstate = 'online'
        self.inventory = Room("%s's inventory" % name,
                              "You should not be here.")
        self.cmdict = cmdict
        self.passhash = passhash
        self.session = {}
        TargettableObject.__init__(self, sdesc, name, adjs, room)

    def receivedLine(self, line, info):
        """Receive a single line of input to process and act upon."""
        cmd, rest = head_word_split(line)
        logging.debug("cmd is %r." % cmd)
        func = self.cmdict[cmd.lower()]
        logging.debug("Command found in cmdict, function is %r" % func)
        func(self, rest, info)

    def disconnect(self):
        '''Notify the listeners that we are being disconnected.'''
        for listener in self.listeners.copy(): #copy because we mutate it
            listener.disconnecting(self)
            #no self.removeListener(listener) here because it's a little silly
            #to not have it implied.

    def __getstate__(self):
        state = TargettableObject.__getstate__(self)
        state['connstate'] = 'offline'
        return self

    def __setstate__(self, state):
        TargettableObject.__setstate__(self, state)
        self.room.remove(self)

    @staticmethod
    def get(name, passhash):
        #XXX: refactor this to telnet.py?
        """Get the avatar referred to by name, but only if its passhash is
        equal.

        Throws KeyErrors if the name is garbage.
        """
        if not Player.exists(name):
            raise KeyError("name is not the name of a player")
        avatar = TargettableObject._name_registry[name]
        if passhash != avatar.passhash:
            raise BadPassword()
        return avatar

class ExitObject(MUDObject):
    """An exit."""

    def __init__(self, direction, room, target_room, exit_desc = None):
        self.direction = direction
        self.target_room = target_room
        self.exit_desc = direction if exit_desc is not None else exit_desc
        MUDObject.__init__(self, room)

class BadPassword(Exception):
    pass

