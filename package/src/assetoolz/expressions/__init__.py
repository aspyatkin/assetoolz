import os
from utils import load_file


class BaseExpression(object):
    def __init__(self, asset, match):
        self._asset = asset
        self._match = match

    @property
    def match(self):
        return self._match

    @property
    def asset(self):
        return self._asset


class BaseIncludeExpression(BaseExpression):
    def __init__(self, asset, match, include_folder, include_pattern,
                 param="p_include_path"):
        super(BaseIncludeExpression, self).__init__(asset, match)
        self._include_path = self.match.group(param)
        self._dependency_path = os.path.join(self.asset._settings.assets,
                                             include_folder,
                                             self._include_path)
        self._dependency_path = os.path.join(
            os.path.dirname(self._dependency_path),
            include_pattern % os.path.basename(self._dependency_path)
        )
        self.asset.add_dependency(self._dependency_path)

    def __call__(self, **opts):
        cache_entry = self.asset._tool_cache.find_entry(self._dependency_path)
        if cache_entry:
            return load_file(cache_entry.target)
        return ""

    @staticmethod
    def get_regex_params():
        return ["p_include_path"]
