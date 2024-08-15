import sys
from . import Ale

for path_ale in sys.argv[1:]:
    with open("temp.txt","w") as temp:
        print(Ale.from_path(path_ale), file=temp)