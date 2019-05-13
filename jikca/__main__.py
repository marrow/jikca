from os import getlogin, getpid

from anyio import aopen, run
from aioconsole import get_standard_streams

from jikca.protocol import JikcaGameSession


async def main():
	STDIN, STDOUT = await get_standard_streams()
	
	# The name of each interactive session is a combination of username and process ID.  E.g. "amcgregor-53758"
	invoke = JikcaGameSession(f"{getlogin()}-{getpid()}")  # Has no location until authenticated.
	
	async for line in STDIN:
		if line == "\d":  # Session has ended.
			return
		
		STDOUT.write(line)  # Echo the line back.
		await invoke(line)  # Actually interrogate the line.
		


if __name__ == '__main__':
	run(main)
