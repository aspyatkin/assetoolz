import os
from assetoolz.cache import Cache
from assetoolz.models import CacheEntry
from assetoolz.utils import get_file_hash, save_file, load_file
import shutil
import codecs
from assetoolz.compiler import ExpressionProcessor
from assetoolz.expressions import stylesheets, scripts, html
import subprocess
import tempfile


class AssetCollection(object):
    def __init__(self, file_list, settings):
        self._assets = []
        self._settings = settings
        for path in file_list:
            res = get_asset_objects(path, settings)
            if type(res) is list:
                for asset in res:
                    self._assets.append(asset)
                    self._assets[-1]._collection = self
                    self._assets[-1]._settings = settings
            else:
                if res is None:
                    continue
                self._assets.append(res)
                self._assets[-1]._collection = self
                self._assets[-1]._settings = settings

    def find_asset(self, path, lang):
        for asset in self._assets:
            if asset._path == path and asset._lang == lang:
                return asset
        return None

    def pick_dependencies(self):
        print("Picking dependencies...")
        for asset in self._assets:
            print(asset)
            asset.parse()
            print("Dependencies %s\n" % asset._dependencies)

        self._assets = DependencyResolver.topological_sort(self._assets)
        print(str(self._assets))

    def build(self):
        print("Building assets...")
        for asset in self._assets:
            asset.compile(self._settings.force)


class DependencyResolver(object):
    @staticmethod
    def topological_sort(assets_unsorted):
        assets_sorted = []

        while len(assets_unsorted) > 0:
            acyclic = False
            for asset in assets_unsorted:
                for dependency in asset._dependencies:
                    if dependency in assets_unsorted:
                        break
                else:
                    acyclic = True
                    assets_unsorted.remove(asset)
                    assets_sorted.append(asset)

            if not acyclic:
                raise RuntimeError("A cyclic dependency occurred")

        return assets_sorted


class Asset(object):
    FILE = 0
    STRING = 1

    def __init__(self, resource_type, path, lang):
        self._resource_type = resource_type
        self._path = path
        self._lang = lang
        self._collection = None
        self._settings = None
        self._dependencies = []
        self._tool_cache = Cache()
        self._flag_modified = False

    def is_partial(self, path):
        return os.path.basename(path).startswith("_")

    def get_target_path(self, **opts):
        common_prefix = os.path.commonprefix([
            self._path,
            self._get_source_dir()])
        path_part = self._path[len(common_prefix)+1:]
        if 'hash' in opts:
            parts = os.path.splitext(path_part)
            new_filename = '%s-%s' % (parts[0], opts['hash'])
            path_part = '%s%s' % (new_filename, parts[1])
        if 'change_extension' in opts:
            new_ext = opts['change_extension']
            parts = os.path.splitext(path_part)
            path_part = '%s%s' % (parts[0], new_ext)
        if 'lang' in opts and not(opts['lang'] is None):
            lang = opts['lang']
            parts = os.path.splitext(path_part)
            path_part = '%s-%s%s' % (parts[0], lang, parts[1])
        if self.is_partial(path_part):
            target_path = os.path.join(self._get_partials_dir(), path_part)
        else:
            target_path = os.path.join(self._get_target_dir(), path_part)
        return target_path

    def __repr__(self):
        return '<%s> {path: %s, lang: %s}' % (self.__class__.__name__,
                                              self._path,
                                              str(self._lang))

    def add_dependency(self, path, lang=None):
        dependency = self._collection.find_asset(path, lang)
        if dependency:
            if dependency not in self._dependencies:
                self._dependencies.append(dependency)
        else:
            print("Couldn't find dependency with path %s" % path)

    def __eq__(self, other):
        return self._path == other._path and self._lang == other._lang

    def __ne__(self, other):
        return self._path != other._path and self._lang != other._lang

    def parse(self):
        self._parse()

    def dependencies_modified(self):
        for dep_asset in self._dependencies:
            if dep_asset._flag_modified:
                return True
        return False

    def compile(self, force=False):
        if self._resource_type == Asset.FILE:
            cache_entry = self._tool_cache.find_entry(self._path, self._lang)

            file_modified = True if cache_entry is None\
                else cache_entry.file_modified() or self.dependencies_modified()

            if file_modified or force:
                if cache_entry:
                    if os.path.exists(cache_entry.target):
                        os.remove(cache_entry.target)

                target_path = self._get_target_path()
                self._compile(target_path)

                if cache_entry:
                    cache_entry.target = target_path
                    self._tool_cache.update(cache_entry)
                    print('Updated %s' % str(self))
                else:
                    cache_entry = CacheEntry(self._path, target_path, self._lang)
                    self._tool_cache.add(cache_entry)
                    print('Created %s' % str(self))
                self._flag_modified = True
            else:
                print('Cached %s' % str(self))
        else:
            print("String asset")


class StringAsset(Asset):
    def __init__(self, path, lang=None):
        super(StringAsset, self).__init__(Asset.STRING, path, lang)
        self._data = None


class TextAsset(Asset):
    def __init__(self, path, lang=None):
        super(TextAsset, self).__init__(Asset.FILE, path, lang)
        self._data = None

        split = os.path.splitext(path)
        self._basename = split[0]
        self._extension = split[1]

    def load(self):
        with codecs.open(self._path, "r", "utf_8") as f:
            self._data = f.read()

    def save(self, path):
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        save_file(path, self._data)


class StylesheetAsset(TextAsset):
    @staticmethod
    def supported_extensions():
        return ['.css', '.scss']

    @staticmethod
    def get_languages(settings):
        return settings.stylesheets.languages

    def _get_partials_dir(self):
        return os.path.join(self._settings.partials, 'stylesheets')

    def _get_source_dir(self):
        return self._settings.stylesheets.source

    def _get_target_dir(self):
        return self._settings.stylesheets.target

    def _get_target_path(self):
        return self.get_target_path(hash=get_file_hash(self._path, True))

    def _parse(self):
        self.load()
        self._processor = ExpressionProcessor(self, [
            stylesheets.ImageUrlExpression,
            stylesheets.IncludeExpression
        ])
        self._processor.parse()

    def minify(self):
        temp_path = tempfile.mkdtemp()

        source_file = os.path.join(temp_path, "source.css")
        save_file(source_file, self._data)
        target_file = os.path.join(temp_path, "target.css")

        proc = subprocess.Popen(
            [
                "java",
                "-jar",
                self._settings.yuicompressor_file,
                "--type",
                "css",
                "-o",
                target_file,
                source_file
            ],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )
        out, err = proc.communicate()
        print(out)
        print(err)

        self._data = load_file(target_file)
        shutil.rmtree(temp_path)

    def _compile(self, target_path):
        self._processor.compile(self._settings, target_path)
        if self._settings.minify and not self.is_partial(target_path):
            print('Minifying %s' % str(self))
            self.minify()
        self.save(target_path)


class ScriptAsset(TextAsset):
    @staticmethod
    def supported_extensions():
        return ['.js', '.coffee']

    @staticmethod
    def get_languages(settings):
        return settings.scripts.languages

    def _get_partials_dir(self):
        return os.path.join(self._settings.partials, 'scripts')

    def _get_source_dir(self):
        return self._settings.scripts.source

    def _get_target_dir(self):
        return self._settings.scripts.target

    def _get_target_path(self):
        return self.get_target_path(
            hash=get_file_hash(self._path, True),
            change_extension='.js'
        )

    def _parse(self):
        self.load()
        self._processor = ExpressionProcessor(self, [
            scripts.IncludeExpression,
            scripts.ScriptUrlExpression,
            scripts.AppConfExpression
        ])
        self._processor.parse()

    def minify(self):
        temp_path = tempfile.mkdtemp()

        source_file = os.path.join(temp_path, "source.js")
        save_file(source_file, self._data)
        target_file = os.path.join(temp_path, "target.js")

        proc = subprocess.Popen(
            [
                "java",
                "-jar",
                self._settings.yuicompressor_file,
                "--type",
                "js",
                "-o",
                target_file,
                source_file
            ],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )
        out, err = proc.communicate()
        print(out)
        print(err)

        self._data = load_file(target_file)
        shutil.rmtree(temp_path)

    def compile_coffee(self):
        temp_path = tempfile.mkdtemp()

        source_file = os.path.join(temp_path, "source.coffee")
        save_file(source_file, self._data)
        target_file = os.path.join(temp_path, "source.js")

        proc = subprocess.Popen(
            [
                "coffee",
                "-c",
                source_file
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        out, err = proc.communicate()
        print(out)
        print(err)

        self._data = load_file(target_file)
        shutil.rmtree(temp_path)

    def _compile(self, target_path):
        self._processor.compile(self._settings, target_path)
        if self._extension == '.coffee':
            print("Using CoffeeScript Compiler for %s" % str(self))
            self.compile_coffee()
        if self._settings.minify and not self.is_partial(target_path):
            print("Minifying %s" % str(self))
            self.minify()
        self.save(target_path)


class HtmlAsset(TextAsset):
    @staticmethod
    def supported_extensions():
        return ['.html']

    @staticmethod
    def get_languages(settings):
        return settings.html.languages

    def _get_partials_dir(self):
        return os.path.join(self._settings.partials, 'html')

    def _get_source_dir(self):
        return self._settings.html.source

    def _get_target_dir(self):
        return self._settings.html.target

    def _get_target_path(self):
        return self.get_target_path(lang=self._lang)

    def _parse(self):
        self.load()
        self._processor = ExpressionProcessor(self, [
            html.IncludeExpression,
            html.StylesheetUrlExpression,
            html.ScriptUrlExpression,
            html.ImageUrlExpression,
            html.AppConfExpression,
            html.I18nExpression
        ])
        self._processor.parse()

    def minify(self):
        temp_path = tempfile.mkdtemp()

        source_file = os.path.join(temp_path, "source.html")
        save_file(source_file, self._data)
        target_file = os.path.join(temp_path, "target.html")

        proc = subprocess.Popen(
            [
                "java",
                "-jar",
                self._settings.htmlcompressor_file,
                "--type",
                "html",
                "--mask",
                "*.html",
                "-o",
                target_file,
                source_file,
                "--remove-intertag-spaces"
            ],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE
        )
        out, err = proc.communicate()
        print(out)
        print(err)

        self._data = load_file(target_file)
        shutil.rmtree(temp_path)

    def _compile(self, target_path):
        self._processor.compile(self._settings, target_path)
        if self._settings.minify and not self.is_partial(target_path):
            print('Minifying %s' % str(self))
            self.minify()
        self.save(target_path)


class BinaryAsset(Asset):
    def __init__(self, path, lang=None):
        super(BinaryAsset, self).__init__(Asset.FILE, path, lang)

    @staticmethod
    def supported_extensions():
        return ['.png', '.jpg', '.gif']

    @staticmethod
    def get_languages(settings):
        return settings.images.languages

    def _get_partials_dir(self):
        return os.path.join(self._settings.partials, 'images')

    def _get_source_dir(self):
        return self._settings.images.source

    def _get_target_dir(self):
        return self._settings.images.target

    def _get_target_path(self):
        return self.get_target_path(hash=get_file_hash(self._path, True))

    def _parse(self):
        pass

    def _compile(self, target_path):
        if not os.path.exists(os.path.dirname(target_path)):
            os.makedirs(os.path.dirname(target_path))
        shutil.copy(self._path, target_path)


def get_asset_objects(path, settings):
    asset_classes = [
        BinaryAsset,
        StylesheetAsset,
        HtmlAsset,
        ScriptAsset
    ]

    file_ext = os.path.splitext(path)[1]
    for asset_class in asset_classes:
        if file_ext in asset_class.supported_extensions():
            langs = asset_class.get_languages(settings)
            if langs is None:
                return asset_class(path, None)
            else:
                return [asset_class(path, lang) for lang in langs]

    return None
