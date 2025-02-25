import sys, pathlib
import pyale

if __name__ == "__main__":

	if not len(sys.argv) > 1:
		print(f"Usage: {pathlib.Path(__file__).name} file_path.ale [another_file.ale ...]", file=sys.stderr)
		sys.exit(1)

	for path_ale in sys.argv[1:]:
		try:
			ale = pyale.Ale.from_path(path_ale)
		except Exception as e:
			print(f"Skipping {path_ale}: {e}")
			continue

		print(ale.to_formatted_string())
		
		print("")
		print(f"Ale Path:  {path_ale}")
		print(f"ALE Header Columns ({len(ale.columns)}):  {[col for col in ale.columns]}")
		print(f" ALE Event Columns ({len(ale.events.columns)}):  {ale.events.columns}")
		print(f"        ALE Events ({len(ale.events)}):  {[e for e in ale.events]}")