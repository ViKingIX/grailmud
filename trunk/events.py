'''This class has some base classes for events.'''

class BaseEvent(object):
    '''The root of all events.'''

    def collapseToText(self, state, obj):
        raise NotImplementedError("Base class.")

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
