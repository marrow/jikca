syntax = r'^pemit (?P<recipients>[^=]+)=(?P<message>.+)$'

def pemit(caller, recipients, message, reference=None):
    recipients = search(caller, recipients, kind=db.Character, flags=['online'])
    
    for character in recipients:
        character.connection.write(unescape(caller, message + "\s(normal)", reference))

pemit.safe = True
pemit.complete = True
