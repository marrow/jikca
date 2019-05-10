syntax = r'^(?:l|look)(?: at)?(?: the)?(?: (?P<target>[^ ]+))?(?: (?P<view>.+))?$'

def look(caller, target='here', view=None):
    target = search(caller, target).all()
    
    if not target:
        commands.pemit(caller, caller, """\c(red)!!! Unable to find target object.""")
        return
    
    target = target[0]
    
    if not view:
        # TODO: Use the target's template, the region's template, or the master template.
        commands.pemit(caller, caller, db.Object.get(2).properties['templates'].get(target.__class__.__name__, db.Object.get(2).properties['templates']['__default']), target)
    
    else:
        view = view.strip()
        
        if 'views' not in target.properties:
            commands.pemit(caller, caller, """\c(red)!!! Target does not have any views.""")
            return
        
        if view not in target.properties['views']:
            commands.pemit(caller, caller, """\c(red)!!! Target does not have view '%s'""" % ( view, ))
            return
        
        commands.pemit(caller, caller, target.properties['views'][view], target)
        
    caller.character.properties['__last_object'] = target.id

look.safe = True
look.complete = True
