syntax = r'^@(?P<name>\S+) (?P<targets>[^=]+) ?= ?(?P<value>.+)?$'

def property(caller, name, targets, value=None):
    targets = search(caller, targets)
    
    if name == 'name' and value is None:
        commands.pemit(caller, caller, """\c(red)You can not unset the name property.""")
        return
    
    for target in targets:
        if name in target.safe:
            setattr(target, name, value)
        
        elif value is None:
            if name in target.properties:
                del target.properties[name]
                commands.pemit(caller, caller, """\c(green)Property unset on %r.""" % (target, ))
                
            return
        
        else:
            target.properties[name] = value
        
        commands.pemit(caller, caller, """\c(green)Property updated on %r.""" % (target, ))

property.safe = True
property.complete = True
