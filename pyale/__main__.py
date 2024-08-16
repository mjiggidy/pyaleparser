import sys
from . import Ale

for path_ale in sys.argv[1:]:
    ale = Ale.from_path(path_ale)
    for thing in ale.events:
        print(thing)