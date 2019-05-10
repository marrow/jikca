# -*- coding: utf-8 -*-

import logging, copy

from twisted.internet.protocol import Factory

from pyoomush.protocol import PyOOMUSHProtocol


log = logging.getLogger('factory')


class PyOOMUSHFactory(Factory):
    protocol = PyOOMUSHProtocol
    service = None
    
    def __init__(self):
        self.namespace = dict(factory=self, service=None, _=None)
        log.debug("Configuring new Factory instance.")
    
    def setService(self, service):
        self.namespace['service'] = self.service = service
        log.debug("Assigning service.")
    
    def __getstate__(self):
        current = self.__dict__
        ns = copy.copy(current['namespace'])
        current['namespace'] = ns
        if ns.has_key('__builtins__'):
            del ns['__builtins__']
        return current
