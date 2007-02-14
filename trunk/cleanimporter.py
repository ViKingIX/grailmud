import sys

class CleanImporter(object):

    def __init__(self, modname):
        self.modname = modname
        self.oldglobals = None
        self.names = None

    def __enter__(self):
        mod = __import__(self.modname)
        components = self.modname.split('.')[1:]
        for comp in components:
            mod = getattr(mod, comp)
        if hasattr(mod, '__all__'):
            self.names = mod.__all__
        else:
            self.names = [name for name in dir(mod) if name[0] != '_']
        
        self.frame = sys._getframe(1)
        self.oldglobals = {}

        for name in self.names:
            if name in self.frame.f_globals:
                self.oldglobals[name] = self.frame.f_globals[name]
            val = getattr(mod, name)
            self.frame.f_globals[name] = val

    def __exit__(self, typ, val, tb):
        for name in self.names:
            del self.frame.f_globals[name]
        self.frame.f_globals.update(self.oldglobals)
