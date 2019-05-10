# -*- coding: utf-8 -*-

import logging, os
from md5 import md5

from pyoomush import model as db, utilities as util

logging.basicConfig(level=logging.INFO, format='%(levelname)-8s %(name)-12s %(message)s')
log = logging.getLogger('application')


db.metadata.bind = "sqlite:///pyoomush.db"
db.metadata.bind.echo = False

db.setup_all()


def main():
    log.info("Creating database layout.")
    db.create_all()
    db.session.flush()
    
    log.info("Creating universe.")
    
    universe = db.Object(l=1, r=2, name="Universe", description="A starless void through which you can see nothing.  You float, weightless and alone, and wonder why the hells you jumped into a fissure with that stupid book...")
    db.session.flush()
    
    master = db.Room(name="Brain", description="It's squishy.")
    universe.attach(master)
    
    master.properties['welcome'] = """\n\s(bold)Welcome to PyOOMUSH.\n"""
    master.properties['firstconnect'] = """Welcome, %N!\nYou have \s(bold)never\s(normal) previously connected."""
    master.properties['connect'] = """Welcome back, %%N.\nYou last connected from %(host)s on %(date)s at %(time)s."""
    master.properties['oconnect'] = "%N fades into a blustery existence, %p clothing whipping around.  Trails of black fog trail with the wind, then fade."
    master.properties['odisconnect'] = "%N vanishes into darkness, %p clothing disturbed by a wind you can not feel."
    master.properties['odark'] = "An unseen presence"
    
    master.properties['templates'] = dict(__default="""\s(bold)\s(underline)$(name)\s(normal) \s(bold)\c(black)\s(hidden)$(__class__.__name__) #$(id)\s(normal)\n$(description)""")
    
    log.info("Creating default user: god/trinity")
    
    god = db.Player(name="God", _password=md5('trinity').hexdigest(), description="An obviously powerful being, %N clearly doesn't wish %p identity to be known.  All you see before you is a radiant pillar of light.  You would have thought that such a bright object--if it can be called that--would hurt your eyes to look directly at.  Reality is different, however, as you feel no need to avert your eyes.")
    universe.attach(god)
    universe.properties['owner'] = god.id
    master.properties['owner'] = god.id
    god.properties['owner'] = god.id
    db.session.flush()
    
    log.info("Creating default user: peon/lowly")
    
    peon = db.Player(name="Peon", _password=md5('lowly').hexdigest())
    universe.attach(peon)
    peon.properties['owner'] = peon.id
    
    log.info("Adding default commands.")
    
    # TODO: Load default commands into the brain.
    
    for entry in os.listdir('environments/default/commands'):
        if entry[-3:] != ".py": continue
        
        f = file('environments/default/commands/%s' % (entry, ))
        cmd = db.Function(name=entry[:-3], source=f.read())
        cmd.syntax = cmd.source.splitlines()[0][11:-1]
        master.attach(cmd)
        cmd.properties['owner'] = god.id
        
        log.info("Imported command %r with syntax %s.", entry[:-3], cmd.source.splitlines()[0][9:])
    
    log.info("Default layout created.")


if __name__ == '__main__':
    main()
