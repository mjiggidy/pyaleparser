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
	def _from_parser(cls, parser:typing.Iterable):

		ale_heading = cls()

		for idx, line in parser:
			
			if not line:
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

	@classmethod
	def default_columns(cls):

		return cls([
			"Name",
			"Tape",
			"Start",
			"Duration"
		])
	
	@classmethod
	def _from_parser(cls, parser:typing.Iterable):

		ale_columns = cls()

		for idx, line in parser:
			if not line:
				if not ale_columns:
					raise ValueError(f"Line {idx+1}: Encountered unexpected empty line before ALE columns")
				else:
					break

			ale_columns.extend(line.split('\t'))
		
		return ale_columns
	
	def __str__(self) -> str:
		output = self.KEYWORD + "\n"
		output += "\t".join(str(col) for col in self) + "\t"
		output += "\n"
		return output


class AleEvents(collections.UserList):
	"""A list of ALE events"""

	KEYWORD = "Data"
	"""ALE Keyword signifying the beginning of the events list"""

	def __init__(self, events, columns:typing.Optional[AleColumns]=None):

		super().__init__(events)

		if isinstance(events, self.__class__):
			self._columns = AleColumns([col for col in events.columns])
		elif columns:
			self._columns = AleColumns([col for col in columns])
		else:
			self._columns = AleColumns.default_columns()
		
	def _pad_event(self, event):
		cols = len(self.columns)
		return event[:cols] + [""] * (cols - len(event))
	
	def __str__(self) -> str:
		output = "Data\n"
		for event in self.data:
			output += "\t".join(self._pad_event(event)) + "\t\n"
		
		return output
	
	@property
	def columns(self) -> AleColumns:
		return self._columns


	@classmethod
	def _from_parser(cls, parser:typing.Iterable, columns:AleColumns):

		ale_events = list()

		for idx, line in parser:
			if not line:
				break

			fields = line.split('\t')

			if not len(fields) == len(columns):
				raise ValueError(f"Line {idx+2}: Found {len(fields)} fields but expected {len(columns)}")
			
			ale_events.append(fields)
		
		return cls(ale_events, columns=columns)
	
	def __iter__(self):
		return iter({col: str(event[idx]) for idx, col in enumerate(self.columns)} for event in self.data)

class Ale:
	"""An Avid Log Exchange"""

	def __init__(self, *, ale_heading:typing.Optional[AleHeading]=None, ale_columns:typing.Optional[AleColumns]=None, ale_events:typing.Optional[AleEvents]=None):
		
		self._heading    = AleHeading(ale_heading) or AleHeading.default_heading()
		self._ale_events = AleEvents(ale_events) if ale_events else AleEvents(columns=ale_columns)

	@property
	def heading(self):
		return self._heading
	
	@property
	def columns(self):
		return self._ale_events.columns
	
	@property
	def events(self) -> AleEvents:
		return self._ale_events
	
	@classmethod
	def from_path(cls, file_path:str):
		"""Load an ALE from a given file path"""

		with open(file_path) as file_stream:
			return cls.from_stream(file_stream)

	@classmethod
	def from_stream(cls, file_stream:typing.TextIO):
		"""Load an ALE from a text-based input stream"""

		parser = enumerate(l.rstrip("\t\n") for l in file_stream.readlines())

		ale_heading = None
		ale_columns = None
		ale_events  = None

		for idx, line in parser:
			
			if line == AleHeading.KEYWORD:
				if ale_heading:
					raise ValueError(f"Encountered duplicate Header definition on line {idx+1}")
				ale_heading = AleHeading._from_parser(parser)
			
			elif line == AleColumns.KEYWORD:
				if not ale_heading:
					raise ValueError(f"Encountered Column definition before Heading on line {idx+1}")
				ale_columns = AleColumns._from_parser(parser)
			
			elif line == AleEvents.KEYWORD:
				if not ale_heading or not ale_columns:
					raise ValueError(f"Encountered entries list before header data on line {idx+1}")
				ale_events = AleEvents._from_parser(parser, columns=ale_columns)

			else:
				raise ValueError(f"Unexpected content on line {idx + 1}: {line}")
		
		return cls(ale_heading=ale_heading, ale_events=ale_events)
	
	def __repr__(self) -> str:
		return f"<ALE {self.heading} {len(self.columns)} Columns; {len(self.events)} Events>"
	

	def __str__(self) -> str:
		return "\n".join([
			str(self.heading), str(self.columns), str(self.events)
		])
	
	def __iter__(self):
		return iter(self.events)
	