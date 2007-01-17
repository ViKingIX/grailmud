from grail2.multimethod import Multimethod

class Foo(object):
    pass

class Bar(Foo):
    pass

class Baz(Bar):
    pass

class Qux(Baz):
    pass

class Fee(Foo):
    pass

class Fie(Fee, Foo):
    pass

class Foe(Foo):
    pass

sentinel = object()

basecase = Multimethod()

@basecase.register(object, object, object)
def basecase(x, y, z):
    return sentinel

def test_basecase():
    assert basecase('foo', 2480, object) is sentinel
    assert basecase(5789, 'baz', Foo()) is sentinel

simple_dispatch = Multimethod()

@simple_dispatch.register(Bar)
def simple_dispatch(x):
    return "Bar"

@simple_dispatch.register(Fee)
def simple_dispatch(x):
    return "Fee"

@simple_dispatch.register(Foe)
def simple_dispatch(x):
    return "Foe"

def test_simple_dispatch():
    assert simple_dispatch(Bar()) == "Bar"
    print '\n'.join('%r: %r' % kv for kv in simple_dispatch.__dict__.items())
    res = simple_dispatch(Fee())
    print res
    assert res == "Fee"
    assert simple_dispatch(Foe()) == "Foe"

