from __future__ import absolute_import
from models import CacheEntry
import datetime
import db
import os


class Cache(object):
    def __new__(cls, commit=False):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Cache, cls).__new__(cls)
            cls.instance.entries = CacheEntry.query.all()
        return cls.instance

    def is_modified(self, source, target):
    	for entry in self.entries:
    		if entry.source == source:
    			return datetime.datetime.fromtimestamp(os.path.getmtime(source)) > entry.last_modified or\
    				entry.target != target
    	return False

    def update(self, source, target):
    	for entry in self.entries:
    		if entry.source == source:
    			entry.target = target
    			entry.update_last_modified()
    			entry.update_checksum()
    			db.db_session.commit()
    			return

    	cache_entry = CacheEntry(path, output)
    	db.db_session.add(cache_entry)
    	db.db_session.commit()