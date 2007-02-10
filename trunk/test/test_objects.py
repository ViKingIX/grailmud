__copyright__ = """Copyright 2007 Sam Pointon"""

__licence__ = """
This file is part of grailmud.

grailmud is free software; you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation; either version 2 of the License, or (at your option) any later
version.

grailmud is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
grailmud (in the file named LICENSE); if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301  USA
"""

from grail2.objects import MUDObject, TargettableObject, NamedObject, Player
from grail2.events import BaseEvent

class ListenerHelper(object):

    def __init__(self, obj):
        self.received = []
        self.flushed = False
        self.obj = obj
        self.obj.listener = self

    def register(self, obj):
        assert obj is self.obj
        assert self in obj.listeners

    def unregister(self, obj):
        assert obj is self.obj
        assert self not in obj.listeners

    def listenToEvent(self, obj, event):
        assert obj is self.obj
        self.received.append(event)

    def eventListenFlush(self, obj):
        assert obj is self.obj
        self.flushed = True

def test_register():
    obj = MUDObject(None)
    obj.addListener(ListenerHelper(obj))

def test_equality():
    m = MUDObject(None)
    assert m == m
    assert MUDObject(None) != m

def test_hashability():
    s = set([MUDObject(None), MUDObject(None)])
    assert len(s) == 2

class TesterForListening(object):

    def setUp(self):
        self.obj = MUDObject(None)
        self.obj.addListener(ListenerHelper(self.obj))
        
    def test_unregister(self):
        self.obj.removeListener(self.obj.listener)

    def test_event_passing(self):
        self.obj.receiveEvent(BaseEvent())
        assert self.obj.listener.received == [BaseEvent()]

    def test_event_flushing(self):
        self.obj.eventFlush()
        assert self.obj.listener.flushed

    def test_bad_unregister(self):
        self.obj.listeners.remove(self.obj.listener)
        try:
            self.obj.removeListener(self.obj.listener)
        except ValueError:
            pass
        else:
            assert False

    def test_bad_register(self):
        try:
            self.obj.addListener(self.obj.listener)
        except ValueError:
            pass
        else:
            assert False
