import sys, pathlib
from pyaleparser import Ale

USAGE = f"Usage: {pathlib.Path(__file__).name} input_file.ale [another.ale ...]"

if __name__ == "__main__":

	good = 0
	baad = 0

	if len(sys.argv) < 2:
		print(USAGE, file=sys.stderr)
		sys.exit(1)
	
	for path_ale in pathlib.Path(sys.argv[1]).rglob("*.ale"):

		try:
			ale = Ale.from_path(path_ale)
			good += 1
		except Exception as e:
			print(f"{pathlib.Path(path_ale).name}:  {e}")
			baad += 1
		else:
			print(f"{pathlib.Path(path_ale).name}:  Valid with {len(ale.columns)} column(s) and {len(ale.events)} event(s)")
	
	print(f"{good=} {baad=}")