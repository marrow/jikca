syntax = r'^(?:say |\" ?)(?P<message>.+)$'

def say(caller, message):
    """Display a message with a specific format."""
    
    if 'mute' in caller.character.flags:
        commands.pemit(caller, caller, "\c(red)!!! Unable to speak, you are muted.")
        return
    
    # If you are flagged 'dark' (invisible), everyone hears you as a disembodied voice.
    sender = '%N' if 'dark' not in caller.character.flags else db.Object.get(2).properties['odark']
    actions = {
            '?': ('ask', 'asks'),
            '!': ('exclaim', 'exclaims'),
            None: ('say', 'says')
        }
    action = actions.get(message[-1], actions[None])
    
    # Send the message to everyone but you.
    recipients = search(caller, within=caller.character.location, not_within=[caller.character], kind=db.Character, flags=['!deaf'])
    commands.pemit(caller, recipients, '%s %s, "%s"' % (sender, action[1], message))
    
    # You hear yourself talk.  This is called "echo".
    commands.pemit(caller, caller, 'You %s, "%s"' % (action[0], message))

say.safe = True
say.complete = True
