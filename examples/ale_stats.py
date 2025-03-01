import sys, pathlib
from aleparser import Ale
from aleparser.defaults import DEFAULT_FILE_EXTENSION

USAGE = f"{pathlib.Path(__file__)} folder_with_ales"

if __name__ == "__main__":

	if not len(sys.argv) > 1:
		print(USAGE, file=sys.stderr)
		sys.exit(1)
	
	path_ale_folder = sys.argv[1]

	if not pathlib.Path(path_ale_folder).is_dir():
		print(f"This does not appear to be a valid directory: {path_ale_folder}")
		print(USAGE)
		sys.exit(2)

	for path_ale in pathlib.Path(path_ale_folder).rglob(f"*{DEFAULT_FILE_EXTENSION}"):

		if path_ale.name.startswith("."):
			# Skip resource forks
			continue

		try:
			ale_desc = repr(Ale.from_path(path_ale))
		except Exception as e:
			ale_desc = str(e)

		print(f"{path_ale.name.rjust(32)[:32]}  :  {ale_desc}")