syntax = r'^\+check (?P<characters>.+)$'

def checkCharacter(caller, characters):
    characters = search(caller, characters, within=db.Object.get(1), kind=db.Character, deep=True)
    required = ('sex', 'age', 'description', 'info', 'background', 'race')
    
    for character in characters:
        missing = []
        
        for variable in required:
            if variable not in character.properties or not character.properties[variable]:
                missing.append(variable)
        
        if missing:
            commands.pemit(caller, caller, 'Character #%d "%s" is missing: %r' % (character.id, character.name, missing))
        
        else:
            commands.pemit(caller, caller, 'Character #%d "%s" is OK.' % (character.id, character.name))

checkCharacter.safe = True
checkCharacter.complete = True
