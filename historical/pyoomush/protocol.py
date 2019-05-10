# -*- coding: utf-8 -*-

import logging, re, copy, uuid
from md5 import md5

# from twisted.conch.recvline import HistoricRecvLine
from twisted.conch.telnet import StatefulTelnetProtocol

from pyoomush import globals as glob, model as db, utilities as util
from pyoomush.exceptions import *
from pyoomush.utilities import AttributeDictionary


log = logging.getLogger('protocol')


class PyOOMUSHProtocol(StatefulTelnetProtocol):
    """PyOOMUSHProtocol - The PyOOMUSH protocol."""
    
    def __init__(self, *args, **kw):
        self.uuid = None
        self.character = None
        self.environment = dict()
    
    def write(self, text=None, *args, **kw):
        if not text:
            self.sendLine("")
            return
        
        if args:
            assert not kw, "You can not specify both position- and name-based arguments!"
            text = text % args
        
        elif kw:
            text = text % kw
        
        for line in text.splitlines():
            self.transport.write(str(line) + "\r\n")
    
    def connectionMade(self):
        for i in glob.__all__:
            self.environment[i] = getattr(glob, i)
        
        peer = self.transport.getPeer()
        self.uuid = uuid.uuid1()
        
        log.info("Client connection from %s:%d -- %s", peer.host, peer.port, self.uuid)
        glob.clients[self.uuid] = self
        
        glob.commands.pemit(self, self, db.Object.get(2).properties['welcome'])
    
    def connectionLost(self, reason):
        peer = self.transport.getPeer()
        
        log.info("Client disconnect by %s:%d -- %s", peer.host, peer.port, self.uuid)
        log.debug("Client disconnect reason: %r", reason)
        
        if self.character:
            self.character.connection = None
            if 'online' in self.character.flags: self.character.flags.remove('online')
            db.session.flush()
            
            glob.commands.emit(self, db.Object.get(2).properties['odisconnect'])
        
        del glob.clients[self.uuid]
    
    def do(self, command):
        try:
            executables = []
            
            if self.character:
                executables.extend(list(glob.search(self, within=self.character, kind=db.Executable)))
                executables.extend(list(glob.search(self, within=self.character.location, kind=db.Executable)))
            
            executables.extend(list(glob.search(self, within=db.Object.get(2), kind=db.Executable)))
            
            for executable in executables:
                if isinstance(executable, db.Trigger): continue
                
                if hasattr(executable, 'syntax'):
                    match = re.search(str(executable.syntax), command, re.M)
                    if match:
                        executable(self, **match.groupdict())
                        db.session.flush()
                        return True
                
                elif executable.name == command:
                    executable(self)
                    db.session.flush()
                    return True
        
        except Exception, e:
            log.exception("Error when calling '%s'.", command)
            self.write(util.unescape(self, "\c(red)!!! ") + "%s", e.msg if hasattr(e, 'msg') else e.message)
            return True
        
        return False
    
    def lineReceived(self, line):
        line = line.strip()
        
        if not line or line.startswith("//"):
            return
        
        log.debug("%s > %s", self.uuid, line)
        if not self.do(line):
            if self.character and '__last_statement' in self.character.properties and line == self.character.properties['__last_statement']:
                self.write("Repeating a failed action and expecting a different result is the definition of madness.")
            else:
                self.write("I'm sorry, I don't know what you mean by '%s'.", line)
        
        if self.character:
            self.character.properties['__last_statement'] = line
        
        self.write()