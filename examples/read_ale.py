import sys, pathlib
import pyale

if __name__ == "__main__":

	if not len(sys.argv) > 1:
		print(f"Usage: {pathlib.Path(__file__).name} file_path.ale", file=sys.stderr)
		sys.exit(1)

	ale = pyale.Ale.from_path(sys.argv[1])
	event_columns = ale.events.columns
	print(f"ALE Header Columns ({len(ale.columns)}): {[col for col in ale.columns]}")
	print(f" ALE Event Columns ({len(event_columns)}): {event_columns}")
	print(f"        ALE Events ({len(ale.events)}): {[e for e in ale.events]}")
	print(f"Using trailing tab? {ale.columns.with_trailing_tab}")