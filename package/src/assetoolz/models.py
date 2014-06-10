from .db import Model
from sqlalchemy import Column, Integer, String, DateTime
import os
import datetime
from .utils import get_file_hash


class CacheEntry(Model):
    __tablename__ = "cache"
    id = Column(Integer, primary_key=True)
    source = Column(String(512))
    target = Column(String(512))
    lang = Column(String(10), nullable=True)
    last_modified = Column(DateTime)
    checksum = Column(String(64))

    def __init__(self, source, target, lang=None):
        self.source = source
        self.target = target
        self.lang = lang
        self.update_last_modified()
        self.update_checksum()

    def update_checksum(self):
        self.checksum = get_file_hash(self.source)

    def update_last_modified(self):
        self.last_modified = datetime.datetime.fromtimestamp(
            os.path.getmtime(self.source))

    def __repr__(self):
        return "%d - s:'%s', t:'%s', m:'%s', c:'%s'" % (
            self.id, self.source, self.target, self.last_modified,
            self.checksum)

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return self.id != other.id

    def file_modified(self):
        if not os.path.exists(self.target):
            return True
        source_last_mod = datetime.datetime.fromtimestamp(
            os.path.getmtime(self.source))
        if source_last_mod > self.last_modified:
            return True
        return False
