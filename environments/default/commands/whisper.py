syntax = r'^whisper (?P<recipients>[^=]+)=(?P<message>.+)$'

def whisper(caller, recipients, message):
    """Display a message with a specific format."""
    
    if 'mute' in caller.character.flags:
        commands.pemit(caller, caller, "\c(red)!!! Unable to speak, you are muted.")
        return
    
    # If you are flagged 'dark' (invisible), everyone hears you as a disembodied voice.
    sender = '%N' if 'dark' not in caller.character.flags else db.Object.get(2).properties['odark']
    
    # Build a list of non-deaf recipients and send the message to them.
    recipients = search(caller, recipients, within=caller.character.location, kind=db.Character, flags=['!deaf'])
    commands.pemit(caller, recipients, '%s whispers, "%s"' % (sender, message))
    
    # Find everyone else in the room and tell them that you've been whispering.
    others = search(caller, within=caller.character.location, not_within=[caller.character]+recipients.all(), kind=db.Character, flags=['!deaf'])
    commands.pemit(caller, others, "%s whispers something." % (sender, ))
    
    # Finally, echo your whisper.
    commands.pemit(caller, caller, 'You whisper, "%s"' % (message, ))

whisper.safe = True
whisper.complete = True
