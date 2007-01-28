from grail2.events import *

class MyVeryOwnEvent(BaseEvent):
    pass

def test_subclasses():
    assert issubclass(SystemEvent, BaseEvent)
    assert issubclass(GameEvent, BaseEvent)
    assert issubclass(VisibleEvent, BaseEvent)
    assert issubclass(AudibleEvent, BaseEvent)

def test_equality():
    a = MyVeryOwnEvent()
    b = MyVeryOwnEvent()
    assert a == b
    a.foo = "bar"
    assert a != b
    b.foo = "bar"
    assert a == b

def test_not_implemented_collapseToText():
    try:
        BaseEvent().collapseToText(None, None)
    except NotImplementedError:
        pass
    else:
        assert False
