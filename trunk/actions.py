'''Pulls the actions from the definitions files underneath actiondefs.'''
from collections import defaultdict
import os

actiondefpath = os.getcwd() + '/actiondefs'

modulenames = []

for filename in os.listdir(actiondefpath):
    package = os.access(os.path.join(actiondefpath, filename, "__init__.py"),
                                     os.F_OK)
    if filename.endswith('py'):
        module = True
        filename = filename[:-3]
    else:
        module = False
    if module or package:
        modulenames.append(filename)

modules = [getattr(__import__('grail2.actiondefs', fromlist = modulenames),
                   name)
           for name in modulenames]

def get_actions():
    '''Goes over all the actiondef modules and registers the cdict.'''
    cdict = defaultdict()
    for module in modules:
        if hasattr(module, "register"):
            module.register(cdict)
    return cdict
