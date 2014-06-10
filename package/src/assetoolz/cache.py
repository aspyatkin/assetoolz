from .models import CacheEntry
from . import db
import os


class Cache(object):
    def __new__(cls, commit=False):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Cache, cls).__new__(cls)
            cls.instance.entries = CacheEntry.query.all()
        return cls.instance

    def check(self):
        for entry in self.entries:
            if not os.path.exists(entry.source):
                if os.path.exists(entry.target):
                    os.remove(entry.target)
                db.db_session.delete(entry)

        db.db_session.commit()

    def find_entry(self, source, lang=None):
        for entry in self.entries:
            if entry.source == source and entry.lang == lang:
                return entry
        return None

    def add(self, entry):
        self.entries.append(entry)
        db.db_session.add(entry)
        db.db_session.commit()

    def update(self, entry):
        entry.update_last_modified()
        entry.update_checksum()
        db.db_session.commit()
