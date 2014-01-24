from __future__ import absolute_import
from models import CacheEntry


class Cache(object):
    def __new__(cls, commit=False):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Cache, cls).__new__(cls)
            cls.instance.entries = CacheEntry.query.all()
        return cls.instance
