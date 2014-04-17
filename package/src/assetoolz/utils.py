from hashlib import sha256
import codecs
import os
import urlparse


def shorten_digest(hexdigest):
    alphabet = list("0123456789abcdefghijklmnopqrstuvwxyz")
    alpha_len = len(alphabet)

    unique_id = int(hexdigest, 16)
    output = ""
    while unique_id:
        unique_id, digit = divmod(unique_id, alpha_len)
        output += alphabet[digit]
    return output


def get_file_hash(path, unique=False):
    hash = sha256()
    if unique:
        hash.update(os.urandom(32))
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash.update(chunk)
    return shorten_digest(hash.hexdigest())


def get_data_hash(data):
    hash = sha256()
    hash.update(data)
    return hash.hexdigest()


def load_file(path):
    data = None
    with codecs.open(path, "r", "utf_8") as f:
        data = f.read()
    return data


def save_file(path, data):
    with codecs.open(path, "w", "utf_8") as f:
        f.write(data)


def make_url_path(base_folder, base_url, path):
    prefix = os.path.commonprefix([
        base_folder,
        path
    ])
    if prefix == base_folder:
        path_part = path[len(prefix)+1:].replace('\\', '/')
        return urlparse.urljoin(base_url, path_part)
    return ''
