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

from grailmud.utils import InstanceTracker, InstanceVariableFactoryObject
import pickle

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

def test_non_equality():
    assert FooClass() != FooClass()

def test_equality():
    obj = FooClass()
    assert obj == obj

def test_pickling_throwing_error():
    obj = FooClass()
    objdump = pickle.dumps(obj)
    FooClass()
    print FooClass.__setstate__
    try:
        newobj = pickle.loads(objdump)
    except RuntimeError:
        pass
    else:
        assert newobj is obj

from grailmud.utils import smartdict

def test_smartdict_expr_evaluation():
    res = ("%('foo'.upper())s" % smartdict())
    print res
    assert res == "FOO"

def test_smartdict_variable_namespace():
    res = ("%(foo.lower())s" % smartdict(foo = 'FOO'))
    print res
    assert res == "foo"
