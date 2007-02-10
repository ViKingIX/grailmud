# pylint: disable-msg= E1101
#pylint doesn't know about our metaclass hackery

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

def promptcolour(colourname = 'normal', chunk = False):
    def fngrabber(func):
        def doer_of_stuff(self, state, obj):
            state.forcePrompt()
            if chunk:
                state.chunk()
            state.setColourName(colourname)
            func(self, state, obj)
        return doer_of_stuff
    return fngrabber
    
class smartdict(dict):
    def __getitem__(self, item):
        #convert to dict to prevent infinite recursion
        return eval(item, globals(), dict(self))

class InstanceTrackingMetaclass(type):
    '''A metaclass that removes some of the boilerplate needed for the
    InstanceTracker class.
    '''

    def __init__(cls, name, bases, dictionary):
        cls._instances = {}
        cls._curnum = 0
        super(InstanceTrackingMetaclass,
              cls).__init__(name, bases, dictionary)

    def __call__(cls, *args, **kwargs):
        res = type.__call__(cls, *args, **kwargs)
        res.add_to_instances()
        return res

    def prefab_instances(cls, instances):
        #XXX: some way to push down to subclasses?
        cls._curnum = max(instances) + 1
        cls._instances = instances

class InstanceTracker(object):
    '''A type that keeps track of its instances.'''

    __metaclass__ = InstanceTrackingMetaclass

    def add_to_instances(self):
        num = 0
        classes = list(self.get_suitable_classes())
        for cls in classes:
            #first, get our number: we can't poach numbers from subclasses or
            #sibling classes, though.
            num = max(num, cls._curnum)
        self._number = num
        print self._number
        num = num + 1
        for cls in classes:
            cls._instances[num] = self
            cls._curnum = num

    def remove_from_instances(self):
        for cls in self.get_suitable_classes():
            if self._number in cls._instances:
                del cls._instances[self._number]

    def get_suitable_classes(self):
        for cls in type(self).__mro__:
            if '_instances' in cls.__dict__ and '_curnum' in cls.__dict__:
                yield cls

    def __setstate__(self, state):
        if not hasattr(self, "_number") or \
           self._number not in self._instances:
            self.add_to_instances()
        self.__dict__.update(state)

    #the number faffing around ensures that we survive pickles.
    def __hash__(self):
        return self._number

    def __eq__(self, other):
        return self._number == other._number

class InstanceVariableFactoryMetaclass(type):

    def __init__(cls, name, bases, dictionary):
        cls._instance_variable_factories = {}
        super(InstanceVariableFactoryMetaclass,
              cls).__init__(name, bases, dictionary)

class InstanceVariableFactoryObject(object):

    __metaclass__ = InstanceVariableFactoryMetaclass
    
    def __getattribute__(self, attr):
        #please note, this method took a little while to get right, so don't
        #just change it willy-nilly. if something is here, it is here for a
        #reason, and not a hysterical one.
        if attr not in ('__dict__', '__class__'):
            if attr not in self.__dict__:
                for cls in type(self).__mro__:
                    if attr in getattr(cls, '_instance_variable_factories',
                                       {}):
                        res = cls._instance_variable_factories[attr](self)
                        setattr(self, attr, res)
                        return res

                if not any((attr in cls.__dict__) for cls in type(self).__mro__):
                    raise AttributeError()
            
        return object.__getattribute__(self, attr)

class BothAtOnceMetaclass(InstanceTrackingMetaclass,
                          InstanceVariableFactoryMetaclass):
    pass

class BothAtOnce(InstanceVariableFactoryObject, InstanceTracker):

    __metaclass__ = BothAtOnceMetaclass
