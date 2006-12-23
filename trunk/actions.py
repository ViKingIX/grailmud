from collections import defaultdict

cdict = defaultdict()
for module in ['core', 'look', 'says', 'system', 'who']:
    mod = getattr(__import__('grail2.actiondefs', fromlist = [module]), module)
    mod.register(cdict)
