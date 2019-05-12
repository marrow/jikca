"""Jikca In-Game Object Model"""

from os import getenv as ENV
from typing import NewType, Union

from bson import ObjectId as oid

from marrow.mongo import Document
from marrow.mongo.field import String, Reference
from marrow.mongo.trait import Derived, Queryable


Search = NewType('Search', set)  # TODO: move to a more appropriate location.


class Cached(Document):  # TODO: Move to a more appropriate location.
	"""A mix-in to implement in-memory "singleton" behaviour."""
	
	_cache = {}  # A mapping of identifiers to instantiated Object instances already loaded from DB.
	
	def from_mongo(self, doc):
		if doc is None:
			return None
		
		if doc['_id'] in self.__cache:
			self.__cache[doc['_id']].__data__ = doc  # Update the in-memory cached copy.
			return self.__cache[doc['_id']]
		
		# Some day, clean this up with the "walrus operator" by assigning and returning at the same time:
		# return self.__cache[doc['_id']] := super().from_mongo(doc)
		
		doc = self.__cache[doc['_id']] = super().from_mongo(doc)
		return doc


class Object(Cached, Derived, Queryable):
	"""Attributes, properties, and behaviours common to all in-game objects."""
	
	# ### Metadata
	
	__collection__ = ENV('JIKCA_COLLECTION', 'objects')  # Configurable via JIKCA_COLLECTION environment variable.
	
	# ### Attributes
	
	# id is provided by Identified, which Queryable is a type of.
	
	id: oid = Queryable.id.adapt()  # TODO: hwid to reference the object acting at the moment of creation.
	name: str = String()  # An optional identifier for humans to utilize when referencing this object in-game.
	_location: oid = Reference('Object', name='location')  # Aliased: changing this value has behaviour; see below.
	
	# ### Python Methods
	
	def __str__(self) -> str:
		"""If the object is to be treated as a string, what do we display?
		
		E.g. if you str(self), print(player), str(player.location), etc., etc.
		"""
		
		return self.name
	
	# ### Accessor Properties
	# Behaviours in response to self-change.
	
	@property
	def location(self) -> Object:  # Note, this returns the actual object, not just its ID.
		"""Retrieve the referenced location Object on access."""
		
		if self._location in self._cache:
			return self._cache[self._location]
		
		return self.find_one(self._location)
	
	@location.setter
	def location(self, value:Union[Object,oid]):  # Allow assignment of either an object, or just its ID in isolation.
		"""Move this object to another location."""
		
		# Notify interested parties: the previous location and contents of (old siblings at) that location.
		event = ...  # TODO
		
		for obj in self.siblings & {self.location}:
			...  # TODO
		
		# Update the in-memory reference.
		self._location = value
		
		# Update the persisted (database-stored) value.
		self.update(location=value)  # TODO: Verify it worked! ;^P
		
		# Notify interested parties: the new location and contents of (new siblings at) that location.
		event = ...  # TODO
		
		for sibling in self.siblings & {self.location}:
			...  # TODO
	
	# ### Properties
	
	@property
	def ancestors(self) -> Search:
		"""Retrieve the objects cromprising the path from the root to ourselves."""
		
		path = list()
		current = self
		
		while current:
			path.append(current)
			current = self.location
		
		return Search(set(reversed(path)))
	
	@property
	def contents(self) -> Search:
		"""Retrieve the objects whose location attribute references us as thier container."""
		return Search({Object.from_mongo(doc) for doc in Object.find(parent=self)})
	
	@property
	def descendants(self) -> Search:
		"""Retrieve the contents of ourselves regardless of storage depth."""
		raise NotImplementedError("Recursion denied; pivot graph storage if needed.")
	
	@property
	def siblings(self) -> Search:
		"""Retrieve the contents of our current location excluding ourselves."""
		return Search(self.location.contents - {self})
