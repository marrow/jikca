# -*- coding: utf-8 -*-

__all__ = ['EmptySearchException', 'AmbiguousSearchException']


class EmptySearchException(Exception):
    __str__ = lambda self: "You didn't find what you were looking for."


class AmbiguousSearchException(Exception):
    __str__ = lambda self: "Your query was too ambiguous."
