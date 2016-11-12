syntax = r'^\+who(?:/(?P<switch>wide))?$'

def who(caller, switch=None):
    players = search(caller, within=db.Object.get(1), deep=True, kind=db.Player, flags=['online'])
    
    for player in players:
        commands.pemit(caller, caller, " * $(name) \s(bold)\c(black)($(location.name))", player)

who.safe = True
who.complete = True
