syntax = r'^(?:connect|login|logon|signin|signon) (?P<user>[^ ]+) (?P<password>.+)$'

def connect(caller, user, password):
    from datetime import datetime
    from md5 import md5
    
    try:
        # Look up the player and assign them to the caller.
        # Before this point, the caller did not have a character property.
        log.debug("Players: %r", ["%s %s" % (i.name, i._password) for i in db.Player.query.all()])
        log.debug("Checking for %r %r", user, md5(password).hexdigest())
        
        caller.character = db.Player.query.filter(
                db.and_(db.Player.name.startswith(user), db.Player._password==md5(password).hexdigest())
            ).one()
        
        # Database management stuff.
        # This first line would logically create a recursive loop, but the connection property only actually saves a UUID.
        caller.character.connection = caller
        caller.character.flags.append("online")
        
        # Display a welcome message.
        if '__last_connection' not in caller.character.properties:
            commands.pemit(caller, caller, db.Object.get(2).properties['firstconnect'])
        
        else:
            commands.pemit(caller, caller, db.Object.get(2).properties['connect'] % dict(
                    host = caller.character.properties['__last_connection']['host'],
                    date = caller.character.properties['__last_connection']['when'].strftime('%A %B %e, %Y'),
                    time = caller.character.properties['__last_connection']['when'].strftime("%l:%M %p").strip()
                ))
        
        # Update the last connection information.
        caller.character.properties['__last_connection'] = dict(
                host = caller.transport.getPeer().host,
                when = datetime.now()
            )
        
        caller.character.properties['__last_object'] = caller.character.id
        
        db.session.flush()
        
        recipients = search(caller, within=caller.character.location, not_within=[caller.character], kind=db.Character, flags=['!deaf'])
        commands.pemit(caller, recipients, caller.character.properties['oconnect'] if 'oconnect' in caller.character.properties else db.Object.get(2).properties['oconnect'])
        
        caller.write()
        commands.look(caller)
        
    except:
        log.exception("There was an error while %r was logging in." % (caller, ))
        caller.write("Unknown user or invalid password.  Try again.")

connect.safe = True
connect.complete = True
