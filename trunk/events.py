class BaseEvent(object):

    def collapseToText(self, state, obj):
        raise NotImplementedError("Base class.")

class SystemEvent(BaseEvent):
    pass

class GameEvent(BaseEvent):
    pass

class AudibleEvent(GameEvent):
    pass

class VisibleEvent(GameEvent):
    pass
