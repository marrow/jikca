syntax = r'^\+haunted(?: (?P<locations>.+))?$'

def haunted(caller, locations='here'):
    locations = search(locations, kind=db.Room)
    
    if search(caller, within=locations, kind=db.Character, not_within=[caller.character], flags=['dark', '!deaf']).count():
        pemit(caller, "You feel some sort of presence.")
        return
    
    pemit(caller, "You do not sense a hidden presence.")

haunted.safe = True
haunted.complete = True