import logging

console = logging.getLogger('model')

import os, sys, time
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy import and_, or_, not_

from elixir import *


log = logging.getLogger('compiler')


def create_flag(name):
    flag = Flag.get(name)
    if flag: return flag
    
    return Flag(name=name)


class Alias(Entity):
    using_options(tablename='alias')
    __repr__    = lambda self: "<Alias %s>" % self.name
    
    target      = ManyToOne('Object')
    name        = Field(String(200))


class Flag(Entity):
    using_options(tablename='flag')
    __repr__    = lambda self: "<Flag %s>" % self.name
    
    name        = Field(String(200))
    
    @classmethod
    def normalize(name):
        return name.strip()


class Property(Entity):
    using_options(tablename='properties')
    __repr__    = lambda self: "<Property %s %r>" % ( self.name, self.data )

    node        = ManyToOne('Object')
    name        = Field(String(200))
    data        = Field(PickleType, default=None, deferred=True)


class Object(Entity):
    using_options(tablename='object', inheritance='multi', polymorphic=True, order_by='l')
    __repr__    = lambda self: "<Object #%r '%s'>" % ( self.id, self.name )
    
    safe        = ['name', 'title', 'description', 'desc']
    
    l, r        = Field(Integer, default=0), Field(Integer, default=0)
    location    = ManyToOne('Object')
    contents    = OneToMany('Object', inverse='location')
    
    name        = Field(String(200))
    description = Field(Text)
    
    def _set_desc(self, value):
        self.description = value
    
    desc        = property(lambda self: self.description, _set_desc)
    
    _aliases    = OneToMany('Alias')
    _properties = OneToMany('Property', collection_class=attribute_mapped_collection('name'))
    _flags      = ManyToMany('Flag')
    
    aliases     = association_proxy('_aliases', 'name', creator=lambda name: Alias(name=name))
    properties  = association_proxy('_properties', 'data', creator=lambda name, val: Property(name=name, data=val))
    flags       = association_proxy('_flags', 'name', creator=create_flag)
    
    ancestors   = property(lambda self: Object.query.filter(and_(Object.r > self.r, Object.l < self.l)), doc="Return all ancestors of this object.")
    descendants = property(lambda self: Object.query.filter(and_(Object.l > self.l, Object.r < self.r)), doc="Return all descendants of this object.")
    depth       = property(lambda self: self.ancestors.count() + 1, doc="Return the current object's depth in the tree.")
    siblings    = property(lambda self: (self.location.contents.filter(Object.r < self.r), self.location.contents.filter(Object.l > self.l)), doc="Return two lists; the first are siblings to the left, the second, to the right.")
    
    path        = property(lambda self: ".".join([i.name for i in self.ancestors if i.id != 1] + [self.name]), doc="Return the full path to this object.")
    
    @classmethod
    def stargate(cls, left=None, right=None, value=2, both=None):
        """Open a hole in the left/right structure.  Alternatively, with a negative value, close a hole."""
        
        if both:
            Object.table.update(both, values=dict(l = Object.l + value, r = Object.r + value)).execute()
        
        if left:
            Object.table.update(left, values=dict(l = Object.l + value)).execute()
        
        if right:
            Object.table.update(right, values=dict(r = Object.r + value)).execute()
        
        session.flush()
        
        # Expire the cache of the l and r columns for every Object.
        [session.expire(obj, ['l', 'r']) for obj in session if isinstance(obj, Object)]
    
    def attach(self, node, after=True, below=True):
        """Attach an object as a child or sibling of the current object."""
        
        session.flush()
        
        if self is node:
            raise Exception, "You can not attach a node to itself."
        
        if node in self.ancestors.all():
            raise Exception, "Infinite loops give coders headaches.  Putting %r inside %r is a bad idea." % (node, self)
        
        if node.l and node.r:
            console.warn("l=%d, r=%d", node.l, node.r)
            # Run some additional integrity checks before modifying the database.
            assert node.l < node.r, "This object can not be moved as its positional relationship information is corrupt."
            assert node.descendants.count() == ( node.r - node.l - 1 ) / 2, "This node is missing descendants and can not be moved."
        
        count = ( 1 + node.descendants.count() ) * 2
        transaction = session.begin()
        
        try:
            if below:
                if after: self.stargate(Object.l >= self.r, Object.r >= self.r, count)
                else: self.stargate(Object.l > self.l, Object.r > self.l, count)
            else:
                if after: self.stargate(Object.l > self.r, Object.r > self.r, count)
                else: self.stargate(Object.l >= self.l, Object.r >= self.l, count)

            if not node.l or not node.r:
                # This node is currently unassigned and/or corrupt.
                if below:
                    if after: node.l, node.r = self.r - 2, self.r - 1
                    else: node.l, node.r = self.l + 1, self.l + 2
                    node.location = self
                    transaction.commit()
                    return

                else:
                    if after: node.l, node.r = self.r + 1, self.r + 2
                    else: node.l, node.r = self.l - 2, self.l - 1
                    node.location = self.location
                    transaction.commit()
                    return
            
            # This node was already placed in the tree and needs to be moved.  How far?
            if below:
                if after: delta = self.r - node.r - 1
                else: delta = self.l - node.l + 1
            else:
                if after: delta = self.r - node.r + 2
                else: delta = self.l - node.l - 2

            # Migrate the node and its ancestors to its new location.
            hole = node.l
            self.stargate(value=delta, both=and_(Object.l >= node.l, Object.r <= node.r))

            # Close the resulting hole.
            self.stargate(Object.l >= hole, Object.r >= hole, -count)

            node.location = self

        except:
            transaction.rollback()
            raise

        else:
            transaction.commit()


class Region(Object):
    using_options(tablename='region', inheritance='multi', polymorphic=True)
    __repr__    = lambda self: "<Region #%r %s>" % ( self.id, self.name )
    
    pass


class Room(Object):
    using_options(tablename='room', inheritance='multi', polymorphic=True)
    __repr__    = lambda self: "<%s (Room #%r)>" % ( self.name, self.id )
    
    pass


class Executable(Object):
    using_options(tablename='executable', inheritance='multi', polymorphic=True)
    __repr__    = lambda self: "<Executable #%r %s>" % ( self.id, self.name )
    
    pass


class Trigger(Executable):
    using_options(tablename='trigger', inheritance='multi', polymorphic=True)
    __repr__    = lambda self: "<Trigger #%r %s>" % ( self.id, self.name )
    
    klass       = Field(String(200), default=None)


class Function(Executable):
    using_options(tablename='function', inheritance='multi', polymorphic=True)
    __repr__    = lambda self: "<Function #%r %s>" % ( self.id, self.name )
    
    syntax      = Field(String(250), default="")
    source      = Field(Text)
    
    def compile(self):
        now = time.time()
        
        from pyoomush import globals as glob
        
        code = compile(self.source, repr(self), "exec")
        
        namespace = dict()
        environment = dict()
        for i in glob.__all__:
            environment[i] = getattr(glob, i)
        
        exec code in environment, namespace
        glob.commands[self.name] = namespace[self.name]
        
        if 'syntax' in namespace and namespace['syntax'] != self.syntax:
            self.syntax = namespace['syntax']
            
            session.flush()
        
        log.info("Compilation of the %r function took %f seconds.", self.name, time.time() - now)
    
    def __call__(self, caller, *args, **kw):
        from pyoomush import globals as glob
        if not hasattr(glob.commands, self.name): self.compile()
        glob.commands[self.name](caller, *args, **kw)


class Exit(Executable):
    using_options(tablename='exit', inheritance='multi', polymorphic=True)
    __repr__    = lambda self: "<Exit #%r %s>" % ( self.id, self.name )
    
    target      = ManyToOne('Room')
    
    def __call__(self, namespace):
        exec "commands.exit(self)" in namespace, dict(self=self)


class Character(Object):
    using_options(tablename='character', inheritance='multi', polymorphic=True)
    __repr__    = lambda self: "%s (Character #%r)" % ( self.name, self.id )
    
    home        = ManyToOne('Object')


class Player(Character):
    using_options(tablename='player', inheritance='multi', polymorphic=True)
    
    _password    = Field(Text, colname="password")
    _connection  = Field(String(64), colname="connection")
    
    def _get_connection(self):
        from pyoomush.globals import clients
        
        if self._connection in clients:
            return clients[self._connection]
        
        return None
    
    def _set_connection(self, value):
        if isinstance(value, basestring):
            self._connection = value
            
        else:
            self._connection = value.uuid
    
    connection = property(_get_connection, _set_connection)
    
    def _get_password(self):
        return self._password
    
    def _set_password(self, value):
        from md5 import md5
        self._password = md5(value).hexdigest()
    
    password = property(_get_password, _set_password)
