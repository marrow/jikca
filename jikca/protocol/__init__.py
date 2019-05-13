"""The primary "interactive session" game protocol.

Being interactive fiction, Jikca speaks a "line protocol" which parses and invokes commands in response to individual
lines of input typically entered interactively by a user. At a fundamental level, it's a bare textual socket protocol;
think: telnet.
"""

from typing import Optional

from marrow.mongo.field import Reference

from jikca.types import Callable, Object


class JikcaGameSession(Object):
	async def __call__(self, actor, *line:str):
		"""Process a line of input (single string argument) or multiple strings to treat as space-separated input.
		
		As we do not derive from `Callable`, there is no risk of this being invoked from within the game world.
		
		Examples:
		
			# Look at the location the object the session is puppeting is located within.
			await invoke('look')
			
			# Equivalent to "take book", this is to allow a more UNIX command-line like (argv) invocation.
			await invoke('take', 'book')
			
			# Not overly useful if every component is static, it becomes far more useful when you have variables.
			await invoke('take', obj)
			
			# If you really do need "variable interpolation" to construct a sensible invocation, use f-strings.
			await invoke(f'@{target}{silent} {message}')
		"""
		
		line = ' '.join(line)  # Combine multiple arguments into one string representing the equivalent line of input.
		
		# Identify the calling context.
		this = self.location  # Connections "puppet" (control) the object they are placed within.
		here = this.location  # The location of the puppet, not the connection, is "here".
		
		# Identify the search path and possible commands to invoke.
		path = [this, here]  # TODO: Include any rooms with links `leaking` *to* here.
		candidates = {obj for component in path for obj in component.contents if isinstance(obj, Callable)}
		
		for command in candidates:
			matched, arguments = await command.matches(line)
			if matched: command(self.location or self, **arguments)
