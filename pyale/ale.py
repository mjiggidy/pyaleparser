import collections, typing

class AleHeading(collections.UserDict):
	"""ALE Heading Data"""

	KEYWORD = "Heading"
	"""ALE Keyword signifying the beginning of the heading data"""

	DEFAULT_FILM = {
		"FIELD_DELIM":"TABS",
		"VIDEO_FORMAT":"1080",
		"FILM_FORMAT":"35mm, 4 perf",
		"AUDIO_FORMAT":"48khz",
		"FPS":"24"
	}

	@classmethod
	def default_heading(cls):

		return cls(cls.DEFAULT_FILM)
	
	@classmethod
	def _from_parser(cls, parser:typing.Iterable[tuple[int,str]], stop:list[str]):

		ale_heading = cls()

		for idx, line in parser:
			
			if line in stop:
				break
			
			heading_line = line.split('\t')
			if len(heading_line) != 2:
				raise ValueError(f"Line {idx+1}: Found {len(heading_line)} field(s) when expecting 2:\n{heading_line}")
			
			ale_heading[heading_line[0]] = heading_line[1]
		
		return ale_heading
	
	def __str__(self) -> str:
		output = self.KEYWORD + "\n"
		output += '\n'.join(key + '\t' + val for key,val in self.items())
		output += "\n"
		return output


class AleColumns(collections.UserList):
	"""ALE Column Headers"""

	KEYWORD = "Column"
	"""ALE Keyword signifying the beginning of the column headers definition"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self._with_trailing_tab = True

	@property
	def with_trailing_tab(self) -> bool:
		"""Should the ALE columns end with a trailing tab character"""
		return self._with_trailing_tab
	
	@with_trailing_tab.setter
	def with_trailing_tab(self, use_trailing_tab:bool):
		self._with_trailing_tab = bool(use_trailing_tab)

	@classmethod
	def default_columns(cls):

		return cls([
			"Name",
			"Tape",
			"Start",
			"Duration"
		])
	
	@classmethod
	def _from_parser(cls, parser:typing.Iterable[tuple[int,str]], stop:list[str]):

		ale_columns = cls()

		for idx, line in parser:
			if line in stop:
				if not ale_columns:
					raise ValueError(f"Line {idx+1}: Encountered unexpected empty line before ALE columns")
				else:
					break

			if line.endswith("\t"):
				ale_columns.with_trailing_tab = True
				line = line[:-1]
			else:
				ale_columns.with_trailing_tab = False

			ale_columns.extend(line.split('\t'))
		
		return ale_columns
	
	def __str__(self) -> str:
		output = self.KEYWORD + "\n"
		output += "\t".join(str(col) for col in self)
		if self.with_trailing_tab:
			output += "\t"
		output += "\n"
		return output


class AleEvents(collections.UserList):
	"""A list of ALE events"""

	def __init__(self, initlist=None):
		
		if initlist and not all(self._is_valid_item(event) for event in initlist):
			raise TypeError("The events list only accepts objects of type `AleEvent`")
		
		return super().__init__(initlist)

	KEYWORD = "Data"
	"""ALE Keyword signifying the beginning of the events list"""
		
	def _pad_event(self, event):
		cols = len(self.columns)
		return event[:cols] + [""] * (cols - len(event))
	
	#def __str__(self) -> str:
	#	output = "Data\n"
	#	for event in self.data:
	#		output += "\t".join(self._pad_event(event)) + "\t\n"
	#	
	#	return output
	
	@property
	def columns(self) -> list[str]:
		unique_columns = set()
		for event in self:
			[unique_columns.add(col) for col in event.columns]
			
		return list(unique_columns)


	@classmethod
	def _from_parser(cls, parser:typing.Iterable[tuple[int,str]], columns:AleColumns):

		ale_events = list()

		for idx, line in parser:
			if not line:
				break
			
			# If column headers line had a trailing tab, ensure the entries did too
			# We'll strip it off and catch a mismatch it later when we check field count
			if columns.with_trailing_tab and line.endswith("\t"):
				line = line[:-1]
			
			fields = line.split('\t')

			if not len(fields) == len(columns):
				raise ValueError(f"Line {idx+2}: Found {len(fields)} fields but expected {len(columns)}")
			
			ale_events.append(AleEvent(zip(columns, fields)))
		
		return cls(ale_events)
	
	def extend(self, other):
		
		# Only allow `AleEvent`s
		if not all(self._is_valid_item(event) for event in other):
			raise TypeError("The events list only accepts objects of type `AleEvent`")
		
		return super().extend(other)
	
	def append(self, item):

		# Only allow `AleEvent`
		if not self._is_valid_item(item):
			raise TypeError("The events list only accepts objects of type `AleEvent`")
		
		return super().append(item)
	
	def __add__(self, other):

		# Only allow `AleEvent`
		if not self._is_valid_item(other):
			raise TypeError("The events list only accepts objects of type `AleEvent`")
		
		return super().__add__(other)
	
	def __iadd__(self, other):
		
		# Only allow `AleEvent`
		if not self._is_valid_item(other):
			raise TypeError("The events list only accepts objects of type `AleEvent`")

		return super().__iadd__(other)
	
	def _is_valid_item(self, other) -> bool:
		"""Validate a list item on add"""

		return isinstance(other, AleEvent)

class AleEvent(collections.UserDict):
	"""An ALE Event contains all fields defined for an event"""

	@property
	def columns(self) -> list[str]:
		return list(self.keys())
	
	def __setitem__(self, key, item):

		key  = str(key)
		item = str(item)

		if not key.strip():
			# Column name needs to be reasonable
			raise ValueError("Column name must not be empty or purely whitespace")
		if not item.strip():
			# Simply ignore empty values; do not add them
			return

		return super().__setitem__(key, item)

class Ale:
	"""An Avid Log Exchange"""

	def __init__(self, *, heading:typing.Optional[AleHeading]=None, columns:typing.Optional[AleColumns]=None, events:typing.Optional[AleEvents]=None):
		
		self._heading = AleHeading(heading) or AleHeading.default_heading()
		self._columns = AleColumns(columns) if columns is not None else AleColumns.default_columns()
		self._events  = AleEvents(events)   if events  is not None else AleEvents([])

	@property
	def heading(self) -> AleHeading:
		return self._heading
	
	@property
	def columns(self) -> AleColumns:
		return self._columns
	
	@property
	def events(self) -> AleEvents:
		return self._events
	
	@classmethod
	def from_path(cls, file_path:str):
		"""Load an ALE from a given file path"""

		with open(file_path) as file_stream:
			return cls.from_stream(file_stream)

	@classmethod
	def from_stream(cls, file_stream:typing.TextIO):
		"""Load an ALE from a text-based input stream"""

		parser = enumerate(l.rstrip("\n") for l in file_stream.readlines())

		ale_heading = None
		ale_columns = None
		ale_events  = None

		for idx, line in parser:
			
			if line == AleHeading.KEYWORD:
				if ale_heading:
					raise ValueError(f"Encountered duplicate Header definition on line {idx+1}")
				ale_heading = AleHeading._from_parser(parser, stop=["",AleColumns.KEYWORD])
			
			elif line == AleColumns.KEYWORD:
				if not ale_heading:
					raise ValueError(f"Encountered Column definition before Heading on line {idx+1}")
				ale_columns = AleColumns._from_parser(parser, stop=["",AleEvents.KEYWORD])
			
			elif line == AleEvents.KEYWORD:
				if not ale_heading or not ale_columns:
					raise ValueError(f"Encountered entries list before header data on line {idx+1}")
				ale_events = AleEvents._from_parser(parser, columns=ale_columns)

			else:
				raise ValueError(f"Unexpected content on line {idx + 1}: {line}")
		
		return cls(heading=ale_heading, columns=ale_columns, events=ale_events)
	
	def __repr__(self) -> str:
		return f"<ALE {self.heading} {len(self.columns)} Columns; {len(self.events)} Events>"
	

	def __str__(self) -> str:
		return "\n".join([
			str(self.heading), str(self.columns), str(self.events)
		])
	
	def __iter__(self):
		return iter(self.events)