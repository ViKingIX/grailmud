# pylint: disable-msg= E1101
#pylint doesn't know about our metaclass hackery
from grail2.orderedset import OSet

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
        cls._instances = OSet()
        super(InstanceTrackingMetaclass,
              cls).__init__(name, bases, dictionary)

    def __call__(cls, *args, **kwargs):
        res = type.__call__(cls, *args, **kwargs)
        res.add_to_instances()
        return res

class InstanceTracker(object):
    '''A type that keeps track of its instances.'''

    __metaclass__ = InstanceTrackingMetaclass

    def add_to_instances(self):
        #there used to be a small buglet here: objects were being put into
        #_instances repeatedly. using an ordered set fixed this.
        for cls in self.get_suitable_classes():
            cls._instances.append(self)

    def remove_from_instances(self):
        for cls in self.get_suitable_classes():
            cls._instances.remove(self)

    def get_suitable_classes(self):
        for cls in type(self).__mro__:
            if '_instances' in cls.__dict__:
                yield cls

    def __setstate__(self, state):
        if self not in self._instances:
            self.add_to_instances()
        self.__dict__.update(state)

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
