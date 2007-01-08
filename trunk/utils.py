
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
        return eval(item, globals(), self)

def in_rooms(obj, rooms):
    #This actually turns out to be stupid and redundant.
    #in_rooms(obj, rooms) -> obj.room in rooms
    for room in rooms:
        if obj in room:
            return True
    return False
