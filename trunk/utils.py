# pylint: disable-msg= E1101
#pylint doesn't know about our metaclass hackery
def monkeypatch(cls):
    def patchergrabber(patcher):
        name = patcher.__name__
        oldfunc = getattr(cls, name)
        def doer_of_stuff(*args, **kwargs):
            oldfunc(*args, **kwargs)
            patcher(*args, **kwargs)
        setattr(cls, name, doer_of_stuff)
        return doer_of_stuff
    return patchergrabber

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

def in_rooms(obj, rooms):
    #This actually turns out to be stupid and redundant.
    #in_rooms(obj, rooms) -> obj.room in rooms
    for room in rooms:
        if obj in room:
            return True
    return False

class InstanceTracker(object):
    '''A type that keeps track of its instances.'''
    class __metaclass__(type):

        def __init__(cls, name, bases, dictionary):
            cls._instances = []
            type.__init__(cls, name, bases, dictionary)

        def __call__(cls, *args, **kwargs):
            #XXX: this probably ought to be a weakref.
            res = type.__call__(cls, *args, **kwargs)
            cls._instances.append(res)
            return res

    def __setstate__(self, state):
        if self not in self._instances:
            self._instances.append(self)
        self.__dict__.update(state)
