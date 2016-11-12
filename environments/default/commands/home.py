syntax = r'^\+home$'

def home(caller):
    if 'link' not in caller.character.properties:
        commands.pemit(caller, caller, "\c(red)!!! You have not linked yourself to a home.")
        return
    
    commands.teleport(caller, db.Object.get(caller.character.properties['link']))

home.safe = True
home.complete = True
