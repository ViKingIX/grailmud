# pylint: disable-msg=C0103
#pylint and its finickity names...
import logging
from grail2.strutils import head_word_split
from grail2.rooms import Room

class MUDObject(object):
    """An object in the MUD."""
    #Instance variables: listeners, room.

    def receiveEvent(self, event):
        """Receive an even in the MUD."""
        for listener in self.listeners:
            listener.listenToEvent(self, event)

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
            self.removeListener(listener)
            obj.addListener(listener)

class TargettableObject(MUDObject):
    """A tangible object, that can be generically targetted."""
    #Additional instance variables: sdesc, name, adjs.
    
    def match(self, attrs):
        """Check to see if a set of attributes is applicable for this object."""
        return (len(attrs) == 1 and self.name in attrs) or \
               self.adjs.issuperset(attrs)

class Player(TargettableObject):
    """A player avatar."""

    def __init__(self, name, sdesc, adjs, cmdict, room):
        self.listeners = set()
        self.name = name
        self.sdesc = sdesc
        self.adjs = adjs | set([name])
        self.cmdict = cmdict
        self.room = room
        self.connstate = 'online'
        self.inventory = Room("%s's inventory" % name,
                              "You should not be here.")

    def receivedLine(self, line, info):
        """Receive a single line of input to process and act upon."""
        cmd, rest = head_word_split(line)
        logging.debug("cmd is %r." % cmd)
        func = self.cmdict[cmd.lower()] #XXX: hardcoded
        logging.debug("Command found in cmdict, function is %r" % func)
        func(self, rest, info)

class ExitObject(MUDObject):
    """An exit."""

    def __init__(self, direction, room, target_room, exit_desc = None):
        self.listeners = set()
        self.direction = direction
        self.room = room
        self.target_room = target_room
        self.exit_desc = direction if exit_desc is None else exit_desc

class PlayerCatalogue(object):
    """A bare-bones database of players."""

    def __init__(self):
        self.byname = {}
        self.passhashes = {}

    def add(self, avatar, passhash):
        """Register a new player."""
        self.byname[avatar.name] = avatar
        self.passhashes[avatar.name] = passhash
