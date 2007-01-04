# pylint: disable-msg=C0103
#pylint and it's finickity names...
'''Pulls the actions from the definitions files underneath actiondefs.'''
from collections import defaultdict

cdict = defaultdict()
modules = ['core', 'look', 'says', 'system', 'who', 'setting', 'deaf']
actiondefs = __import__('grail2.actiondefs', fromlist = modules)

for module in modules:
    getattr(actiondefs, module).register(cdict)
