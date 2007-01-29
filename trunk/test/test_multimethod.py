from grail2.multimethod import Multimethod, Signature

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

def test_signature_creation():
    for typetuple in [(Foo, object, Bar),
                      (Baz, Qux),
                      (object, object, str),
                      ((str, object), Foo)]:
        assert Signature(typetuple).tsig == typetuple

def test_signature_supertyping_success():
    for s1, s2 in [((object,), (Foo,)),
                   ((Foo,), (Foo,)),
                   ((Foo,), (Baz,))]:
        assert Signature(s1) >= Signature(s2)
        assert Signature(s1).supertypes(Signature(s2))
        assert Signature(s2) <= Signature(s1)

def test_signature_supertyping_failure():
    for s1, s2 in [((Foo, object), (Baz,)),
                   ((Fie,), (Foo,))]:
        assert not (Signature(s1) >= Signature(s2))
        assert not (Signature(s1).supertypes(Signature(s2)))
        assert not (Signature(s2) <= Signature(s1))

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

def test_more_complicated_dispatch():
    more_complicated_dispatch = Multimethod()

    @more_complicated_dispatch.register(object, object)
    def more_complicated_dispatch(x, y):
        pass

    @more_complicated_dispatch.register(object, str)
    def more_complicated_dispatch(x, y):
        pass

    @more_complicated_dispatch.register(object, int)
    def more_complicated_dispatch(x, y):
        pass

    #print '\n'.join(repr(s) for s in more_complicated_dispatch.signatures)
    assert more_complicated_dispatch.signatures == \
                                               [Signature((object, str)),
                                                Signature((object, int)),
                                                Signature((object, object))]
