'''Pulls the actions from the definitions files underneath actiondefs.'''
from collections import defaultdict

modulenames = ['core', 'look', 'says', 'system', 'who', 'setting', 'deaf',
               'emote', 'helpfiles', 'targetting']
modules = [getattr(__import__('grail2.actiondefs', fromlist = modulenames),
                   name)
           for name in modulenames]

def get_actions():
    '''Goes over all the actiondef modules and registers the cdict.'''
    cdict = defaultdict()
    for module in modules:
        module.register(cdict)
    return cdict
