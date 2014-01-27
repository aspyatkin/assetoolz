from hashlib import sha256
import codecs


def get_file_hash(path):
    hash = sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash.update(chunk)
    return hash.hexdigest()


def get_data_hash(data):
    hash = sha256()
    hash.update(data)
    return hash.hexdigest()


def load_file(path):
    data = None
    with codecs.open(path, "r", "utf_8") as f:
        data = f.read()
    return data
