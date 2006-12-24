import logging
from grail2.strutils import head_word_split

class MUDObject(object):
    #Instance variables: listeners, room.

    def receiveEvent(self, event):
        for listener in self.listeners:
            listener.listenToEvent(self, event)

    def eventFlush(self):
        for listener in self.listeners:
            listener.eventListenFlush(self)

    def addListener(self, listener):
        listener.register(self)
        self.listeners.add(listener)

    def removeListener(self, listener):
        listener.unregister(self)
        self.listeners.remove(listener)

    def transferControl(self, obj):
        for listener in self.listeners:
            self.removeListener(listener)
            obj.addListener(listener)

class TargettableObject(MUDObject):
    #Additional instance variables: sdesc, name, adjs.
    
    def match(self, attrs):
        return (len(attrs) == 1 and self.name in attrs) or \
               self.adjs.issuperset(attrs)

class Player(TargettableObject):

    def __init__(self, conn, name, sdesc, adjs, cmdict, room):
        self.listeners = set()
        self.name = name
        self.sdesc = sdesc
        self.adjs = adjs | set([name])
        self.addListener(conn)
        self.cmdict = cmdict
        self.room = room
        self.primaryconn = conn

    def receivedLine(self, line, info):
        cmd, rest = head_word_split(line)
        logging.debug("cmd is %r." % cmd)
        func = self.cmdict[cmd.lower()] #XXX: hardcoded
        logging.debug("Command found in cmdict, function is %r" % func)
        func(self, rest, info)

class ExitObject(MUDObject):

    def __init__(self, direction, room, target_room, exit_desc = None):
        self.listeners = set()
        self.direction = direction
        self.room = room
        self.target_room = target_room
        self.exit_desc = direction if exit_desc is None else exit_desc
