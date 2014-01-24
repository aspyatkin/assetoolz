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
    file = Column(String(256))
    last_modified = Column(DateTime)
    checksum = Column(String(64))

    def __init__(self, path):
        self.file = path
        self.last_modified = datetime.fromtimestamp(
            os.path.getmtime(path))
        self.checksum = get_file_hash(path)
