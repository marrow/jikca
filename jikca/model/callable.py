"""The base definition of all invokable objects."""

from re import Pattern
from typing import AbstractSet, Optional

from bson import ObjectId as oid

from marrow.mongo.field import Set, String, Reference

from .object import Object


class Callable(Object):
	"""The basic definition of an invokable object.
	
	In game terms, this represents an object within the user's search path, which will recognize and match command
	syntax. If matching, the `__call__` method is executed, at a minimum always passing the caller. Additional
	positional arguments are provided by unnamed groups in the matching pattern, and keyword arguments (those passed
	by name) from named groups.
	"""
	
	syntax: AbstractSet[Pattern] = Set(String())  # The input patterns this callable object triggers on.
	
	def __call__(self, caller: Object) -> Optional[str]:
		pass


class Link(Callable):  # TODO: Move to own module.
	"""The core definition of a traversable link between rooms; an exit, portal, bridge, or path.
	
	Example:
	
		# "Dig" a new exit named "north" (triggering on that name) linked to the object (room) with the given ID.
		# Note that the explicit definition of the syntax overrides the default, which is equivalent to this.
		# The default doesn't need to be stored in the database, it's the default.  So don't do that.
		@create Link north #5cd791c58b93805d79cd1ae6 syntax={"n(?:orth)?"}
		@create Link north #5cd791c58b93805d79cd1ae6 south
	"""
	
	syntax: AbstractSet[Pattern] = Callable.syntax.adapt(default={r"{name[:1]}(?:{name[1:]})?"})
	_target: oid = Reference(Object, name='target')  # The opposite side of the link.  Note that links are not bidirectional.
	reflection: str = String(default=None)  # Optionally the name of the opposite direction.
	
	@property
	def target(self):
		return self.find_one(self._target)
	
	@target.setter
	def target(self, obj):
		self._target = obj
		# TODO: Persist.
		# TODO: Notify target of new link.
	
	def __call__(self, caller: Object) -> None:
		"""
		@open <exit;name>[=<destination>[, <return;exit;name>][, <here>]]
		@open north=#27,,#32
		
		dig <room name> [name of the exit out of current room] [name of exit into new room]
		"""
		if 'port' in self:
			self.do('pemit', caller, self['port'])
		 
		if 'oport' in self:
			self.do('pemit', caller.location, self['oport'])
		
		caller.location = self.target
		
		# Identify the 

