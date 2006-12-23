from collections import defaultdict

cdict = defaultdict()
modules = ['core', 'look', 'says', 'system', 'who']
actiondefs = __import__('grail2.actiondefs', fromlist = modules)

for module in modules:
    getattr(actiondefs, module).register(cdict)
