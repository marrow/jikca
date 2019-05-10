syntax = r'^(?P<action>pose |: ?|; ?)(?P<message>.+)$'

def pose(caller, message, action="pose"):
    if 'mute' in caller.character.flags:
        commands.pemit(caller, caller, "\c(red)!!! Unable to pose, you are muted.")
        return
    
    # If you are flagged 'dark' (invisible), everyone hears you as a disembodied voice.
    sender = caller.character.name if 'dark' not in caller.character.flags else db.Object.get(2)['odark']
    
    action = action.strip()
    if action in ['pose', ':']:
        format = "%(sender)s %(message)s"
    elif action == ';':
        format = "%(sender)s%(message)s"
    
    # Send the message to everyone in the room.
    commands.pemit(caller, caller.character.location, format % dict(sender=sender, message=message))

pose.safe = True
pose.complete = True
