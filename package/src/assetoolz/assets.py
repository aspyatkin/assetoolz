import os
from cache import Cache
from models import CacheEntry
from utils import get_file_hash, load_file
import shutil
import codecs
from compiler import ExpressionProcessor
from expressions import stylesheets


class AssetCollection(object):
    def __init__(self, file_list, settings):
        self._assets = []
        self._settings = settings
        for path in file_list:
            self._assets.append(get_asset_object(path))
            self._assets[-1]._collection = self
            self._assets[-1]._settings = settings

    def find_asset(self, path):
        for asset in self._assets:
            if asset._path == path:
                return asset
        return None

    def pick_dependencies(self):
        print("Picking dependencies...")
        for asset in self._assets:
            asset.parse()
            print(asset)
            print("Dependencies %s\n" % asset._dependencies)

        self._assets.sort()
        print(str(self._assets))

    def build(self):
        print("Building assets...")
        for asset in self._assets:
            asset.compile()


class Asset(object):
    def __init__(self, path):
        self._path = path
        self._collection = None
        self._settings = None
        self._dependencies = []
        self._tool_cache = Cache()
        self._flag_modified = False

    def get_target_path(self, **opts):
        common_prefix = os.path.commonprefix([self._path, self._settings.assets])
        path_part = self._path[len(common_prefix)+1:]
        if 'hash' in opts:
            parts = os.path.splitext(path_part)
            new_filename = '%s-%s' % (parts[0], opts['hash'])
            path_part = '%s%s' % (new_filename, parts[1])
        if os.path.basename(path_part).startswith("_"):
            target_path = os.path.join(self._settings.partials, path_part)
        else:
            target_path = os.path.join(self._settings.output, path_part)
        return target_path

    def __repr__(self):
        return '<%s> {path: %s}' % (self.__class__.__name__, self._path)

    def add_dependency(self, path):
        dependency = self._collection.find_asset(path)
        if dependency:
            self._dependencies.append(dependency)
        else:
            print("Couldn't find dependency with path %s" % path)

    def has_dependency(self, asset):
        for dep_asset in self._dependencies:
            if dep_asset == asset:
                return True
        return False

    def __eq__(self, other):
        return self._path == other._path

    def __ne__(self, other):
        return self._path != other._path

    def __cmp__(self, other):
        if other.has_dependency(self):
            # check for cyclic dependency
            assert(not self.has_dependency(other))
            return -1
        if self.has_dependency(other):
            #check for cyclic dependency
            assert(not other.has_dependency(self))
            return 1
        return 0

    def parse(self):
        self._parse()

    def dependencies_modified(self):
        for dep_asset in self._dependencies:
            if dep_asset._flag_modified:
                return True
        return False

    def modified(self, cache_entry=None):
        cache_entry = self._tool_cache.find_entry(self._path)

        return True if cache_entry is None\
            else cache_entry.file_modified() or self.dependencies_modified()

    def compile(self):
        cache_entry = self._tool_cache.find_entry(self._path)

        file_modified = True if cache_entry is None\
            else cache_entry.file_modified() or self.dependencies_modified()

        if file_modified:
            if cache_entry:
                if os.path.exists(cache_entry.target):
                    os.remove(cache_entry.target)

            target_path = self._get_target_path()
            self._compile(target_path)

            if cache_entry:
                cache_entry.target = target_path
                self._tool_cache.update(cache_entry)
                print('Updated asset %s' % str(self))
            else:
                cache_entry = CacheEntry(self._path, target_path)
                self._tool_cache.add(cache_entry)
                print('Created asset %s' % str(self))
            self._flag_modified = True
        else:
            print('Cached asset %s' % str(self))


class TextAsset(Asset):
    def __init__(self, path):
        super(TextAsset, self).__init__(path)
        self._data = None

    def load(self):
        with codecs.open(self._path, "r", "utf_8") as f:
            self._data = f.read()

    def save(self, path):
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        with codecs.open(path, "w", "utf_8") as f:
            f.write(self._data)


class StylesheetAsset(TextAsset):
    @staticmethod
    def supported_extensions():
        return ['.css']

    def _get_target_path(self):
        return self.get_target_path(hash=get_file_hash(self._path))

    def _parse(self):
        self.load()
        self._processor = ExpressionProcessor(self, [
            stylesheets.ImagePathExpression,
            stylesheets.IncludeExpression
        ])
        self._processor.parse()

    def _compile(self, target_path):
        self._processor.compile(self._settings, target_path)
        self.save(target_path)


class ScriptAsset(TextAsset):
    @staticmethod
    def supported_extensions():
        return ['.js']


class HtmlAsset(TextAsset):
    @staticmethod
    def supported_extensions():
        return ['.html']


class BinaryAsset(Asset):
    @staticmethod
    def supported_extensions():
        return ['.png', '.jpg', '.gif']

    def _get_target_path(self):
        return self.get_target_path(hash=get_file_hash(self._path))

    def _parse(self):
        pass

    def _compile(self, target_path):
        if not os.path.exists(os.path.dirname(target_path)):
            os.makedirs(os.path.dirname(target_path))
        shutil.copy(self._path, target_path)


def get_asset_object(path):
    asset_classes = [
        BinaryAsset,
        StylesheetAsset,
        HtmlAsset,
        ScriptAsset
    ]

    file_ext = os.path.splitext(path)[1]
    for asset_class in asset_classes:
        if file_ext in asset_class.supported_extensions():
            return asset_class(path)

    return Asset(path)
