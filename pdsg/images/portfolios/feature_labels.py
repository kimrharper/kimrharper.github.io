def filenamer(directory, segment, prefix="train_"):
	slash = str() if not directory or directory.endswith("/") else "/"
	return f"{directory}{slash}{prefix}{segment}.csv"


class FeatureLabel(object):

	def __hash__(self):
		return hash(self.feature)

	def __lt__(self, other):
		return self.feature < (other.feature if hasattr(other, "feature") else other)

	def __repr__(self):
		return f"{self.datatype:>15}: Line {self.line: 2}, Station {self.station: 4}, Feature {self.feature}"

	@staticmethod
	def read_number(string_piece):
		return int(string_piece[1:])

	def __init__(self, string, datatype="numeric"):
		self.line, self.station, self.feature = (self.read_number(piece) for piece in string.split("_")) 
		self.datatype = "categorical" if datatype == "cat" else datatype


class FeatureLabelSet(set):

	def include(self, headers, datatype="numeric", verbose=True):
		if headers:
			for header in headers.split(","):
				if "_" in header:
					label = FeatureLabel(header, datatype)
					if verbose and label in self:
						print(f"I'm seeing a duplicate for {label}")
					self.add(label)

	def __init__(self, segments=("numeric", "cat", "date"), directory=str(), **keywords):
		for segment in segments:
			with open(filenamer(directory, segment)) as fi:
				self.include(next(fi), datatype=segment, **keywords)


class DatatypeCounter(dict):

	def __repr__(self):
		return "\n".join(f"{datatype:>15}: {self[datatype]:4}" for datatype in sorted(self))
	
	def tally(self, labels):
		for label in labels:
			if label.datatype in self:
				self[label.datatype] += 1
			else:
				self[label.datatype] = 1

	def __init__(self, labels=tuple()):
		super().__init__()
		self.tally(labels)


class FeatureLabelList(list):

	def __repr__(self):
		return "\n".join(map(str, self))

	def __getitem__(self, key):
		result = super().__getitem__(key)
		return type(self)(result) if isinstance(key, slice) else result

	def n_lines(self):
		return len(set(label.line for label in self))

	def __init__(self, values=None, **keywords):
		super().__init__(sorted(FeatureLabelSet(**keywords)) if values is None else values)


class StationLabelDict(dict):
	
	def include(self, labels):
		for label in labels:
			if label.station in self:
				self[label.station].append(label)
			else:
				self[label.station] = FeatureLabelList((label,))

	def are_stations_unique(self):
		return 1 is max(station.n_lines() for station in self.values())

	def datatype_counts(self):
		for station, labels in self.items():
			print(f"\n Station {station:2}  (Line {labels[0].line}):")
			print(DatatypeCounter(labels))

	def feature_counts(self):
		return tuple(len(self[station]) for station in sorted(self))

	def __init__(self, values=None, **keywords):
		super().__init__(self)
		self.include(FeatureLabelSet(**keywords) if values is None else values)
