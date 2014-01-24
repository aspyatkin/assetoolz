from __future__ import absolute_import
from db import Model
from sqlalchemy import Column, Integer, String, DateTime
import os
import datetime
from hashlib import sha256


def get_file_hash(path):
    hash = sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash.update(chunk)
    return hash.hexdigest()


class CacheEntry(Model):
    __tablename__ = "cache"
    id = Column(Integer, primary_key=True)
    source = Column(String(512))
    target = Column(String(512))
    last_modified = Column(DateTime)
    checksum = Column(String(64))

    def __init__(self, source, target):
        self.source = source
        self.target = target
        self.update_last_modified()
        self.update_checksum()

    def update_checksum(self):
        self.checksum = get_file_hash(self.source)

    def update_last_modified(self):
        self.last_modified = datetime.datetime.fromtimestamp(os.path.getmtime(self.source))

    def __repr__(self):
        return "%d - s:'%s', t:'%s', m:'%s', c:'%s'" % (
            self.id, self.source, self.target, self.last_modified,
            self.checksum)
