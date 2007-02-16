import sys

def fetch_module_and_names(modname):
    mod = __import__(modname)
    components = modname.split('.')[1:]
    try:
        for comp in components:
            mod = getattr(mod, comp)
    except AttributeError:
        raise ImportError()
    if hasattr(mod, '__all__'):
        names = mod.__all__
    else:
        names = [name for name in dir(mod) if name[0] != '_']
    return mod, names
    

class CleanImporter(object):
    #this does NOT clobber local names if used inside a function

    def __init__(self, modname):
        self.modname = modname
        self.oldglobals = {}
        self.names = None

    def __enter__(self):
        mod, self.names = fetch_module_and_names(self.modname)
        
        self.frame = sys._getframe(1)

        for name in self.names:
            if name in self.frame.f_globals:
                self.oldglobals[name] = self.frame.f_globals[name]
            val = getattr(mod, name)
            self.frame.f_globals[name] = val

    def __exit__(self, typ, val, tb):
        for name in self.names:
            del self.frame.f_globals[name]
        self.frame.f_globals.update(self.oldglobals)
