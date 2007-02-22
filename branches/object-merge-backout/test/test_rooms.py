from grailmud.rooms import Room, UnfoundError
from grailmud.objects import MUDObject

def test_adding():
    r = Room('A blank room', 'Nothing to see here, move along.')
    obj = MUDObject(None)
    r.add(obj)
    assert obj in r.contents

def test_contains():
    r = Room('A blank room', 'Nothing to see here, move along.')
    obj = MUDObject(None)
    r.contents.add(obj)
    assert obj in r

#XXX: more should be here.
