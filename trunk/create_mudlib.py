# pylint: disable-msg= E1101,W0212
#pylint doesn't know about our metaclass hackery, and complains about the use
#of the leading underscore variables.
"""Instantiate the MUDlib and write it to disk."""
import os
from durus.file_storage import FileStorage
from durus.connection import Connection
from grail2.rooms import Room
from grail2.objects import MUDObject, TargettableObject
from grail2.npcs.chatty import ChattyNPC
from grail2.ticks import Ticker

startroom = Room('An unremarkable moor.',
                 'This moor is extremely bare. Overly so, perhaps. There '
                 'is a definite air of blandness about its grey horizon '
                 'and overcast sky. The ground is anonymous and blank; '
                 'grey dust litters the floor, and that is about all which '
                 'can be said about it. Even the air seems to be steeped in'
                 ' mediocrity - a lukewarm temperature, with no discernable'
                 ' exciting scents.')

eliza = TargettableObject('a bespectacled old lady', 'Eliza',
                          set(['old', 'lady', 'woman']), startroom)
eliza.addListener(ChattyNPC(eliza))
startroom.add(eliza)

if os.access("mudlib.durus", os.F_OK):
    os.remove("mudlib.durus")

connection = Connection(FileStorage("mudlib.durus"))

root = connection.get_root()

root['startroom'] = startroom
root['all_rooms'] = Room._instances
root['all_objects'] = MUDObject._instances
root['ticker'] = Ticker(0.1)

connection.commit()