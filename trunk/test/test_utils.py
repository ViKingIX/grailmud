from grail2.utils import InstanceTracker, InstanceVariableFactoryObject

class FooClass(InstanceTracker):
    pass

def _helper(constructor, cls = None):
    cls = constructor if cls is None else cls

    assert isinstance(constructor(), InstanceTracker)
    
    i = constructor()
    assert i in cls._instances
    i2 = constructor()
    assert i2 in cls._instances

    i.remove_from_instances()
    assert i not in cls._instances

    i2.add_to_instances()
    assert cls._instances.count(i2) == 1

def test_basics_no_subclassing():
    _helper(FooClass)

class FooSubclass(FooClass):
    pass

def test_non_instance_tracking_subclass():
    assert "_instances" in FooSubclass.__dict__

def test_superclass_tracking():
    _helper(FooSubclass, FooClass)
    _helper(FooSubclass)

class FooFactoryClass(InstanceVariableFactoryObject):
    qux = "class"
    pass

def test_instance_variable_factory():
    assert hasattr(FooFactoryClass, "_instance_variable_factories")

def test_default_variables():
    sentinel = object()
    FooFactoryClass._instance_variable_factories['foo'] = lambda self: sentinel
    assert FooFactoryClass().foo is sentinel

def test_setting_default_variables():
    sentinel = object()
    FooFactoryClass._instance_variable_factories['foo'] = lambda self: sentinel
    f = FooFactoryClass()
    assert 'foo' not in f.__dict__
    assert f.foo is sentinel
    assert f.__dict__['foo'] is sentinel

def test_throws_AttributeError():
    try:
        FooFactoryClass().nonexistant
    except AttributeError:
        pass
    else:
        assert False

def test_returns_from___dict___():
    FooFactoryClass._instance_variable_factories['foo'] = lambda s: 'bar'
    f = FooFactoryClass()
    f.foo = "baz"
    assert f.foo == "baz"

class FooFactorySubclass(FooFactoryClass):
    pass

def test_inherited():
    FooFactoryClass._instance_variable_factories['qux'] = lambda s: 'right'
    print FooFactorySubclass().qux
    assert FooFactorySubclass().qux == 'right'