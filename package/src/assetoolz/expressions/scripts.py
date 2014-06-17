from ..expressions import BaseExpression, BaseIncludeExpression
from ..cache import Cache
import os
from ..utils import make_url_path
from ..appconf import AppConfHelper


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


class AppConfExpression(BaseExpression):
    def __init__(self, settings):
        super(AppConfExpression, self).__init__(settings)
        self._key = settings.match.group("p_appconf_key")

    def __call__(self, *args, **opts):
        return str(AppConfHelper().find_replacement(self._key))

    @staticmethod
    def get_regex_params():
        return ["p_appconf_key"]

    @staticmethod
    def get_regex():
        return r"/\*= config (?P<p_appconf_key>[a-zA-Z0-9_\- ]{2,48}(\|[a-zA-Z0-9_\- ]{2,48})*) \*/"


class ResourceUrlExpression(BaseExpression):
    def __init__(self, settings):
        super(ResourceUrlExpression, self).__init__(settings)
        self._key = settings.match.group('p_resource_url')

    def __call__(self, *args, **opts):
        return self.settings.asset._settings.resources.get_url(self._key)

    @staticmethod
    def get_regex_params():
        return ['p_resource_url']

    @staticmethod
    def get_regex():
        return r'/\*= resource_url (?P<p_resource_url>[a-zA-Z0-9_\-]+((/[a-zA-Z0-9_\-]+)*)) \*/'
