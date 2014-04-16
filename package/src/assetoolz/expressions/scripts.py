from assetoolz.expressions import BaseExpression, BaseIncludeExpression
from assetoolz.cache import Cache
import os
from assetoolz.utils import make_url_path


class IncludeExpression(BaseIncludeExpression):
    def __init__(self, settings):
        super(IncludeExpression, self).__init__(
            settings,
            settings.asset._settings.scripts.source,
            "_%s")

    @staticmethod
    def get_regex():
        return r"/\*= include (?P<p_include_path>[a-zA-Z0-9_\-\\\/\.]+\.(js|coffee)) \*/"


class ScriptUrlExpression(BaseExpression):
    def __init__(self, settings):
        super(ScriptUrlExpression, self).__init__(settings)
        self._script_path = settings.match.group("p_script_url")
        self._dependency_path = os.path.join(
            settings.asset._settings.scripts.source,
            self._script_path)
        settings.asset.add_dependency(self._dependency_path)

    def __call__(self, **opts):
        tool_cache = Cache()
        cache_entry = tool_cache.find_entry(self._dependency_path)
        if cache_entry:
            return make_url_path(
                self.settings.asset._settings.cdn_path,
                self.settings.asset._settings.cdn_url,
                cache_entry.target
            )
        return ""

    @staticmethod
    def get_regex_params():
        return ["p_script_url"]

    @staticmethod
    def get_regex():
        return r"/\*= script_url (?P<p_script_url>[a-zA-Z0-9_\-\\\/\.]+\.(js|coffee)) \*/"
