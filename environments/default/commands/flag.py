syntax = r'^@(?P<flag>\S+) (?P<targets>[^=]+)$'

def flag(caller, flag, targets):
    targets = search(caller, targets).all()
    
    if not targets:
        commands.pemit(caller, caller, """\c(red)!!! Unable to find target object.""")
        return
    
    for target in targets:
        if flag in target.flags:
            target.flags.remove(flag)
            commands.pemit(caller, caller, """\c(green)Flag removed from %r.""" % (target, ))
        
        else:
            target.flags.append(flag)
            commands.pemit(caller, caller, """\c(green)Flag added to %r.""" % (target, ))

flag.safe = True
flag.complete = True
