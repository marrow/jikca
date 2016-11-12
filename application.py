# -*- coding: utf-8 -*-

import logging

from twisted import internet
from twisted.application import internet, service, strports
from twisted.internet.protocol import Factory

from pyoomush import model as db, globals as glob, utilities as util
from pyoomush.factory import PyOOMUSHFactory


logging.basicConfig(level=logging.INFO, format='%(levelname)-8s %(name)-12s %(message)s')
log = logging.getLogger('application')



def startup():
    db.metadata.bind = "sqlite:///pyoomush.db"
    db.metadata.bind.echo = False
    
    db.setup_all()
    
    brain = db.Object.get(2)
    
    for fn in db.Function.query.filter(db.Function.location == brain):
        fn.compile()

startup()


application = service.Application("Python Object-Oriented MUSH Server")

factory = PyOOMUSHFactory()

service = strports.service('8100', factory)
factory.setService(service)

service.setServiceParent(application)
