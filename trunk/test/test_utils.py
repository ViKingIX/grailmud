from grail2.utils import InstanceTracker

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
    assert "_instances" not in FooSubclass.__dict__

def test_superclass_tracking():
    _helper(FooSubclass, FooClass)
