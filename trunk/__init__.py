"""A Python MUD."""

#instance is the currently running MUD instance, or None. Either we'd have to do
#some attribute trickery here, or you can only have one instance per Python
#interpreter.
class _LateProxy(object):

    def __init__(self):
        self._bound = False
        self._boundto = None

    def __getattr__(self, name):
        if name in ['_bound', '_boundto', '_bind']:
            return object.__getattr__(self, name)
        if self._bound:
            return getattr(self._boundto, name)
        raise ValueError("Not bound yet!")

    def _bind(self, obj):
        self._bound = True
        self._boundto = obj

instance = _LateProxy()
