import os
from utils import load_file


class ExpressionSettings(object):
    def __init__(self, processor, asset, match):
        self._processor = processor
        self._asset = asset
        self._match = match

    @property
    def processor(self):
        return self._processor

    @property
    def asset(self):
        return self._asset

    @property
    def match(self):
        return self._match


class BaseExpression(object):
    def __init__(self, settings):
        self._settings = settings
        self._php_stub = False
        self._conditional = False
        self._skip_block = False

    @property
    def settings(self):
        return self._settings


class BaseIncludeExpression(BaseExpression):
    def __init__(self, settings, include_folder, include_pattern,
                 param="p_include_path"):
        super(BaseIncludeExpression, self).__init__(settings)
        self._include_path = self.settings.match.group(param)
        self._dependency_path = os.path.join(
            self.settings.asset._settings.assets,
            include_folder, self._include_path)
        self._dependency_path = os.path.join(
            os.path.dirname(self._dependency_path),
            include_pattern % os.path.basename(self._dependency_path)
        )
        self.settings.asset.add_dependency(self._dependency_path)

    def __call__(self, **opts):
        include_asset = self.settings.asset._collection.find_asset(self._dependency_path)
        include_asset._reset(self.settings.processor._varholder)
        include_asset.compile(True)
        cache_entry = self.settings.asset._tool_cache.find_entry(self._dependency_path)
        if cache_entry:
            return load_file(cache_entry.target)
        return ""

    @staticmethod
    def get_regex_params():
        return ["p_include_path"]
