syntax = r'^emit (?P<message>.+)$'

def emit(caller, message):
    commands.pemit(caller, caller.character.location, message)

emit.safe = True
emit.complete = True
