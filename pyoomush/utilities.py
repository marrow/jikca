# -*- coding: utf-8 -*-

import logging, re

from pyoomush import model as db
from sqlalchemy.orm.query import Query


__all__ = ['AttributeDictionary', 'unescape']


log = logging.getLogger('utilities')


class AttributeDictionary(dict):
    def __getattr__(self, name):
        if name in self.__dict__: return self.__dict__[name]
        return self[name]
    
    def __hasattr__(self, name):
        if name in self.__dict__ or name in self: return True
        return False
    
    def __setattr__(self, name, value):
        if name in self.__dict__:
            self.__dict__[name] = value
            return
        
        self[name] = value


def wrap(text, columns=78):
    from textwrap import wrap
    
    lines = []
    for iline in text.splitlines():
        if not iline:
            lines.append(iline)
        else:
            for oline in wrap(iline, columns):
                lines.append(oline)
    
    return "\n".join(lines)


escapes = re.compile(r'(\\[^\\]\([^\)]+\)|\\[^\\]|\\\\|%[^%][\w]?|%%|\$\([^\)]+\)|\$\$)')

escape_slashes = dict(t="\t", n="\n", r="\r")
escape_slashes['s(normal)']     = "\033[0m"

escape_slashes['s(bold)']       = "\033[1m"
escape_slashes['s(intense)']    = "\033[1m"
escape_slashes['s(dim)']        = "\033[2m"
escape_slashes['s(italic)']     = "\033[3m"
escape_slashes['s(underline)']  = "\033[4m"
escape_slashes['s(inverse)']    = "\033[7m"
escape_slashes['s(hidden)']     = "\033[8m"
escape_slashes['s(strike)']     = "\033[9m"

escape_slashes['c(black)']      = "\033[30m"
escape_slashes['c(red)']        = "\033[31m"
escape_slashes['c(green)']      = "\033[32m"
escape_slashes['c(yellow)']     = "\033[33m"
escape_slashes['c(blue)']       = "\033[34m"
escape_slashes['c(magenta)']    = "\033[35m"
escape_slashes['c(cyan)']       = "\033[36m"
escape_slashes['c(white)']      = "\033[37m"
escape_slashes['c(default)']    = "\033[39m"

escape_slashes['b(black)']      = "\033[40m"
escape_slashes['b(red)']        = "\033[41m"
escape_slashes['b(green)']      = "\033[42m"
escape_slashes['b(yellow)']     = "\033[43m"
escape_slashes['b(blue)']       = "\033[44m"
escape_slashes['b(magenta)']    = "\033[45m"
escape_slashes['b(cyan)']       = "\033[46m"
escape_slashes['b(white)']      = "\033[47m"
escape_slashes['b(default)']    = "\033[49m"

#escape_slash_function['c(rainbow)'] - Rotate through all 16 colors.
#escape_slash_function['c(stripe)'] - Alternate between highlight and normal.
#escape_slash_function['c(duotone'] - Alternate between two colors passed as comma-separated escapes.

escape_percents = dict(t="\t", r="\n", b=' ')

# %xN - h=highlight - n=normal - f=flashing - u=underline - i=invert - 

def unescape(caller, text, obj=None):
    from pyoomush.protocol import PyOOMUSHProtocol
    
    if isinstance(caller, PyOOMUSHProtocol): caller = caller.character
    
    gender = caller.properties.get('sex', 'it')[0] if caller else 'i'
    
    local_slashes = dict()
    
    local_percents = dict(
            s = dict(m="he", f="she", i="it", g="they")[gender],        # subjective: he, she, it, they
            o = dict(m="him", f="her", i="it", g="them")[gender],       # objective: him, her, it, them
            p = dict(m="his", f="her", i="its", g="their")[gender],     # posessive: his, her, its, their
            a = dict(m="his", f="hers", i="its", g="theirs")[gender],   # absolute posessive: his, hers, its, theirs
            S = dict(m="He", f="She", i="It", g="They")[gender],        # subjective: he, she, it, they
            O = dict(m="Him", f="Her", i="It", g="Them")[gender],       # objective: him, her, it, them
            P = dict(m="His", f="Her", i="Its", g="Their")[gender],     # posessive: his, her, its, their
            A = dict(m="His", f="Hers", i="Its", g="Theirs")[gender],   # absolute posessive: his, hers, its, theirs
            N = caller.name if caller else 'Anonymous',
            l = ("#%d" % ( caller.location.id, )) if caller else '%l',
            c = caller.properties['__last_command'] if caller and '__last_command' in caller.properties else '%c',
        )
    local_percents['#'] = ("#%d" % ( caller.id, )) if caller else '%#'
    local_percents['@'] = local_percents['#']
    
    def process(match):
        match = match.group(0)
        
        if match == '\\\\': return "\\"
        elif match == '%%': return '%'
        elif match == '$$': return '$'
        
        if match.startswith('\\') and match[1:] in escape_slashes: return escape_slashes[match[1:]]
        if match.startswith('%') and match[1:] in escape_slashes: return escape_slashes[match[1:]]
        
        if match.startswith('\\') and match[1:] in local_slashes: return local_slashes[match[1:]]
        if match.startswith('%') and match[1:] in local_percents: return local_percents[match[1:]]
        
        if match.startswith('$(') and match.endswith(')') and obj:
            match = match[2:-1].split('.')
            log.debug("Attempting to get property %s of %r.", match, obj)
            ref = obj
            for i in match:
                ref = getattr(ref, i, None)
            return unescape(caller, str(ref), obj)
        
        return match
    
    log.debug("Unescaping text: %r", text)
    return escapes.sub(process, text)


class MockCharacter(object):
    def __init__(self, connection):
        self.connection = connection


def search(caller, search=None, within=None, not_within=None, kind=db.Object, flags=[], deep=False):
    from pyoomush.protocol import PyOOMUSHProtocol
    
    # If we are handed a connection, return the associated character.
    if isinstance(search, PyOOMUSHProtocol):
        if search.character: return [search.character]
        return [MockCharacter(search)]
    
    # If we are given an existing query, set our search base to it.
    if isinstance(search, Query): query = search
    else: query = kind.query
    
    # If we are given an Object instance...
    if isinstance(search, db.Object):
        # ...and there is no 'within' clause yet, search within.
        if not within:
            within = search
            search = None
        
        # Otherwise we want to make sure this object matches the other criteria first.
        else:
            query = query.filter(kind.id == search.id)
    
    # If we are given user input...
    if isinstance(search, basestring):
        search = search.strip()
        
        # Allow the user to define a list of options.
        if search[0] == '[' and search[-1] == ']':
            search = [i.strip() for i in search[1:-1].split(',')]
        
        # And if we weren't given a list, make it one anyway.
        else:
            search = [search]
        
        
        ids = []
        names = []
        
        for s in search:
            # If the term begins with a hash symbol, it's a request for a specific ID.
            if s.startswith('#'): ids.append(int(s[1:]))
            
            # Also allow "magic" references.
            elif s in ("self", "me"): ids.append(caller.character.id)
            elif s in ("here"): ids.append(caller.character.location.id)
            elif s in ("_") and '__last_object' in caller.character.properties:
                ids.append(caller.character.properties["__last_object"])
            
            # Otherwise it's a textual search term based on the 'name' property.
            else: names.append(s)
        
        # Build a compound query for the ids and names.
        query = query.filter(db.or_(*([kind.id == i for i in ids] + [kind.name.startswith(i) for i in names])))
    
    # Optionally limit the results to objects contained within a specific parent.
    if within:
        if not deep: query = query.filter(kind.location == within)
        else: query = query.filter(db.and_(kind.l > within.l, kind.r < within.r))
    
    # If 'not_within' is specified and it is a valid database object instance, don't search within.
    if not_within and isinstance(not_within, db.Object):
        query = query.filter(db.not_(db.and_(kind.l > not_within.l, kind.r < not_within.r)))
    
    # Otherwise, if 'not_within' is a list of objects, don't include them in the results.
    elif not_within and isinstance(not_within, list):
        query = query.filter(db.and_(*[kind.id != i.id for i in not_within]))
    
    # Check for the presence, or lack of presence, of a specific set of flags.
    if flags:
        positive = [i for i in flags if not i.startswith('!')]
        negative = [i[1:] for i in flags if i.startswith('!')]
        
        if positive: query = query.filter(kind._flags.any(db.Flag.name.in_(positive)))
        if negative: query = query.filter(db.not_(kind._flags.any(db.Flag.name.in_(negative))))
    
    return query
