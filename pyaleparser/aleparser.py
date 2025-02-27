import collections, typing

class AleHeading(collections.UserDict):
	"""ALE Heading Data"""

	KEYWORD = "Heading"
	"""ALE Keyword signifying the beginning of the heading data"""

	DEFAULT_FILM = {
		"FIELD_DELIM"  : "TABS",
		"VIDEO_FORMAT" : "1080",
		"FILM_FORMAT"  : "35mm, 4 perf",
		"AUDIO_FORMAT" : "48khz",
		"FPS"          : "24"
	}

	@classmethod
	def default_heading(cls):

		return cls(cls.DEFAULT_FILM)
	
	@classmethod
	def _from_parser(cls, parser:typing.Iterable[tuple[int,str]]):

		ale_heading = cls()

		for idx, line in parser:
			
			if not line:
				break
			
			heading_line = line.split('\t')
			if len(heading_line) != 2:
				raise ValueError(f"Line {idx+1}: Found {len(heading_line)} field(s) when expecting 2:\n{heading_line}")
			
			ale_heading[heading_line[0]] = heading_line[1]
		
		return ale_heading
	
	def to_formatted_string(self) -> str:
		"""Format for ALE"""
		return self.KEYWORD + "\n" + ("\n".join(key + "\t" + val for key,val in self.items()))


class AleColumns(collections.UserList):
	"""ALE Column Headers"""

	KEYWORD = "Column"
	"""ALE Keyword signifying the beginning of the column headers definition"""

	def __init__(self, initlist=None):

		if initlist:
			for col in initlist:
				self._is_valid_item(col)
		
		return super().__init__(initlist)
	
	def _is_valid_item(self, col:typing.Any):

		if not isinstance(col, str):
			raise TypeError(f"Column must be a str (got {type(col)})")
		
		# Y'all gon hate me for this
		elif not col.isprintable():
			raise TypeError("Column contains invalid characters")

	@classmethod
	def default_columns(cls):

		return cls([
			"Name",
			"Tape",
			"Start",
			"End",
			"Source File Name"
		])
	
	@classmethod
	def _from_parser(cls, parser:typing.Iterable[tuple[int,str]],):

		ale_columns = cls()

		for idx, line in parser:
			if not line:
				if not ale_columns:
					raise ValueError(f"Line {idx+1}: Encountered unexpected empty line before ALE columns")
				else:
					break

			ale_columns.extend(line.split('\t'))
		
		return ale_columns
	
	def to_formatted_string(self) -> str:
		"""Format for ALE"""
		return self.KEYWORD + "\n" + ("\t".join(str(col) for col in self)) + "\t"


class AleEvents(collections.UserList):
	"""A list of ALE events"""

	def __init__(self, initlist=None):
		
		if initlist:
			for event in initlist:
				self._is_valid_item(event)
		
		return super().__init__(initlist)

	KEYWORD = "Data"
	"""ALE Keyword signifying the beginning of the events list"""
	
	def to_formatted_string(self, columns:typing.Optional[AleColumns]=None) -> str:
		"""Format for ALE"""

		columns = self.columns if columns is None else columns

		output = self.KEYWORD + "\n"
		output += "\n".join([(event.to_formatted_string(columns=columns) + "\t") for event in self])
		return output
	
	@property
	def columns(self) -> AleColumns[str]:
		unique_columns = set()
		for event in self:
			[unique_columns.add(col) for col in event.columns]
			
		return AleColumns(unique_columns)


	@classmethod
	def _from_parser(cls, parser:typing.Iterable[tuple[int,str]], columns:AleColumns, has_trailing_tabs:bool):

		ale_events = list()

		for idx, line in parser:
			if not line:
				break
			
			# If column headers line had a trailing tab, ensure the entries did too
			# We'll strip it off and catch a mismatch it later when we check field count
			if has_trailing_tabs and line.endswith("\t"):
				line = line[:-1]
			
			fields = line.split('\t')

			if not len(fields) == len(columns):
				raise ValueError(f"Line {idx+2}: Found {len(fields)} fields but expected {len(columns)}")
			
			ale_events.append(AleEvent(zip(columns, fields)))
		
		return cls(ale_events)
	
	def extend(self, other):
		
		for event in other:
			self._is_valid_item(event)
		
		return super().extend(other)
	
	def append(self, item):

		self._is_valid_item(item)
		return super().append(item)
	
	def insert(self, i, item):
		
		self._is_valid_item(item)
		return super().insert(i, item)
	
	def __add__(self, other):

		self._is_valid_item(other)
		return super().__add__(other)
	
	def __iadd__(self, other):
		
		self._is_valid_item(other)

		return super().__iadd__(other)
	
	def _is_valid_item(self, other):
		"""Validate a list item on add"""

		if not isinstance(other, AleEvent):
			TypeError("The events list only accepts objects of type `AleEvent`")


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
	
	def to_formatted_string(self, columns:typing.Optional[AleColumns]=None) -> str:
		"Format to string for ALE"
		columns = self.columns if columns is None else columns
		return "\t".join([self.get(col,"") for col in columns])


class Ale:
	"""An Avid Log Exchange"""

	def __init__(self, *, heading:typing.Optional[AleHeading]=None, columns:typing.Optional[AleColumns]=None, events:typing.Optional[AleEvents]=None):
		
		self._heading = AleHeading(heading) if heading is not None else AleHeading.default_heading()
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
	
	def to_path(self, file_path:str):
		"""Write an ALE to a given path"""

		with open(file_path, "w") as file_stream:
			self.to_stream(file_stream)

	def to_stream(self, file_stream:typing.TextIO):
		"""Write an ALE to a text-based file stream"""

		print(self.to_formatted_string(), file=file_stream)
	
	@classmethod
	def from_path(cls, file_path:str):
		"""Load an ALE from a given file path"""

		with open(file_path) as file_stream:
			return cls.from_stream(file_stream)

	@classmethod
	def from_stream(cls, file_stream:typing.TextIO):
		"""Load an ALE from a text-based input stream"""

		parser = enumerate(l.rstrip("\n") for l in file_stream)

		ale_heading = None
		ale_columns = None
		ale_events  = None

		for idx, line in parser:

			# NOTE: ALEs produced by Avid have an empty line between each section
			# I've seen shady third-party ALEs from hacky labs omit the newline
			# Since we don't have an official spec doc for ALE, I'm siding with Avid
			# on this one and not supporting a lack of newlines.  Let me know if
			# this irks you by creating an Issue on GitHub.
			
			if line == AleHeading.KEYWORD:
				if ale_heading:
					raise ValueError(f"Encountered duplicate Header definition on line {idx+1}")
				ale_heading = AleHeading._from_parser(parser)
			
			elif line == AleColumns.KEYWORD:
				if not ale_heading:
					raise ValueError(f"Encountered Column definition before Heading on line {idx+1}")
				ale_columns = AleColumns._from_parser(parser)

				# ALEs produced by Avid have trailing `\t`s at the end of the columns list and each entry.
				# Detect it and remove it for parsing purposes.  We'll put it back on output.
				
				# NOTE: Those third-party ALEs don't always have a trailing `\t` like they should
				# I'm not supporting the out-of-spec lack of `\t` for now, but I'll leave this 
				# here, commented, because I suspect this will be an issue eventually.
				
				#has_trailing_tab = ale_columns and ale_columns[-1] == ""
				has_trailing_tab = True
				
				if has_trailing_tab:
					ale_columns.pop()
			
			elif line == AleEvents.KEYWORD:
				if not ale_heading or not ale_columns:
					raise ValueError(f"Encountered entries list before header data on line {idx+1}")
				ale_events = AleEvents._from_parser(parser, columns=ale_columns, has_trailing_tabs=has_trailing_tab)

			else:
				raise ValueError(f"Unexpected content on line {idx + 1}: {line}")
		
		return cls(heading=ale_heading, columns=ale_columns, events=ale_events)
	
	def __repr__(self) -> str:
		return f"<ALE {self.heading} {len(self.columns)} Columns; {len(self.events)} Events>"
	
	def to_formatted_string(self) -> str:
		"""Format as ALE"""
		return "\n\n".join([
			self.heading.to_formatted_string(),
			self.columns.to_formatted_string(),
			self.events.to_formatted_string(columns=self.columns)
		])
	
	def __iter__(self):
		return iter(self.events)