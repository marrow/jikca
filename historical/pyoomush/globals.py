# -*- coding: utf-8 -*-

import logging, re

from pyoomush import model as db, utilities
from pyoomush.utilities import AttributeDictionary, unescape


__all__ = ['log', 'clients', 'commands', 'db', 'unescape', 'search']


log = logging.getLogger('console')

clients = dict()

commands = AttributeDictionary()

search = utilities.search

