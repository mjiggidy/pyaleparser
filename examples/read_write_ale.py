import sys, pathlib
from aleparser import Ale

USAGE = f"Usage: {pathlib.Path(__file__).name} input_file.ale output_file.ale"

if __name__ == "__main__":

	if len(sys.argv) < 3:
		print(USAGE, file=sys.stderr)
		sys.exit(1)
	
	path_input = sys.argv[1]
	path_output = sys.argv[2]

	if pathlib.Path(path_output).exists():
		print(f"File already exists at output path {path_output}; not overwriting.", file=sys.stderr)
		print(USAGE, file=sys.stderr)
		sys.exit(2)

	try:
		ale = Ale.from_path(path_input)
	except Exception as e:
		print(f"Error reading input ALE: {e}", file=sys.stderr)
		print(USAGE, file=sys.stderr)
		sys.exit(3)
	
	try:
		ale.to_path(path_output)
	except Exception as e:
		print(f"Error writing output file: {e}", file=sys.stderr)
		print(USAGE, file=sys.stderr)
		sys.exit(4)
	
	print(f"ALE with {len(ale.columns)} column(s) and {len(ale.events)} event(s) output to {path_output}")