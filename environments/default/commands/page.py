syntax = r'^(?:p|page)(?:/(?P<switch>emit|pose))? (?P<recipients>[^=]+)=(?P<message>.+)$'

def page(caller, recipients, message, switch=None):
    if 'mute' in caller.character.flags:
        commands.pemit(caller, caller, "\c(red)!!! Unable to page, you are muted.")
        return
    
    recipients = search(caller, recipients, within=db.Object.get(1), not_within=[caller.character], deep=True, kind=db.Character, flags=['!deaf'])
    
    if switch == "pose":
        format = ("From afar, you %s", "From afar, %%N %s")
    elif switch == "emit":
        format = ("From afar, %s", "From afar, %s")
    else:
        format = ('You page, "%s"', '%%N pages, "%s"')
    
    # Send the message to everyone but you.
    commands.pemit(caller, recipients, format[1] % (message, ))
    
    # You hear yourself talk.  This is called "echo".
    commands.pemit(caller, caller, format[0] % (message, ))

page.safe = True
page.complete = True
