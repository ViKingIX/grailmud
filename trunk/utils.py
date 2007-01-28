# pylint: disable-msg= E1101
#pylint doesn't know about our metaclass hackery
from grail2.orderedset import OSet

def promptcolour(colourname = 'normal'):
    def fngrabber(func):
        def doer_of_stuff(self, state, obj):
            state.forcePrompt()
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
        #only add _instances to direct children of InstanceTracker
        if cls.__name__ != 'InstanceTracker' and InstanceTracker in bases:
            cls._instances = OSet()
        type.__init__(cls, name, bases, dictionary)

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
