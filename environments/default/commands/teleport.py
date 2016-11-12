syntax = r'^\+(?:tel|port|teleport)(?P<quiet>/quiet)? (?P<target>.+)$'

def teleport(caller, target, quiet=False, force=False):
    target = search(caller, target).all()
    
    if not target:
        commands.pemit(caller, caller, "\c(red)!!! Unable to find target.")
        return
    
    target = target[0]
    
    if target is caller.character.location:
        commands.pemit(caller, caller, "\c(red)!!! You can not teleport to your current location.")
        return
    
    if not force and 'lock' in target.flags and target.properties['owner'] != caller.character.id: # and 'staff' not in user.groups:
        commands.pemit(caller, caller, "\c(red)!!! You can not teleport into a locked room unless you own it or are a member of staff.")
        return
    
    if not quiet:
        recipients = search(caller, within=caller.character.location, not_within=[caller.character], kind=db.Character, flags=['!deaf'])
        commands.pemit(caller, recipients, '%N has left the room.')
    
    target.attach(caller.character)
    
    if not quiet:
        recipients = search(caller, within=caller.character.location, not_within=[caller.character], kind=db.Character, flags=['!deaf'])
        commands.pemit(caller, recipients, '%N has entered the room.')
        commands.look(caller)

teleport.safe = True
teleport.complete = False
teleport.notes = [
        ('cuttlefish', 'todo', 'Need to use global "otel" property as teleport notification message.'),
        ('cuttlefish', 'todo', 'Need to perform staff group check.')
    ]
