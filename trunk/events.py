'''This class has some base classes for events.'''

class BaseEvent(object):
    '''The root of all events.'''

    chunkable = False

    def collapseToText(self, state, obj):
        raise NotImplementedError("Base class.")

    def __eq__(self, other):
        return type(self) == type(other) and self.__dict__ == other.__dict__

class SystemEvent(BaseEvent):
    '''An event which comes from the system (ie, the implementation).'''
    pass

class GameEvent(BaseEvent):
    '''An event which comes from the game (ie, the world).'''
    pass

class AudibleEvent(GameEvent):
    '''An event you can hear.'''
    pass

class VisibleEvent(GameEvent):
    '''An event you can see.'''
    pass
