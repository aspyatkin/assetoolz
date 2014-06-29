from ..expressions import BaseExpression, BaseIncludeExpression
import os
from ..cache import Cache
from ..utils import make_url_path


class IncludeExpression(BaseIncludeExpression):
    def __init__(self, settings):
        super(IncludeExpression, self).__init__(
            settings,
            settings.asset._settings.stylesheets.source,
            "_%s")

    @staticmethod
    def get_regex():
        return r"/\*= include (?P<p_include_path>[a-zA-Z0-9_\-\\\/\.]+\.(css|scss|sass)) \*/"


class ImageUrlExpression(BaseExpression):
    def __init__(self, settings):
        super(ImageUrlExpression, self).__init__(settings)
        self._image_path = settings.match.group("p_image_url")
        self._dependency_path = os.path.join(
            settings.asset._settings.images.source,
            self._image_path)
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
        return ["p_image_url"]

    @staticmethod
    def get_regex():
        return r"/\*= image_url (?P<p_image_url>[a-zA-Z0-9_\-\\\/\.]+\.(png|gif|jpg)) \*/"


class FontUrlExpression(BaseExpression):
    def __init__(self, settings):
        super(FontUrlExpression, self).__init__(settings)
        self._font_path = settings.match.group("p_font_url")
        self._dependency_path = os.path.join(
            settings.asset._settings.fonts.source,
            self._font_path)
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
        return ["p_font_url"]

    @staticmethod
    def get_regex():
        return r"/\*= font_url (?P<p_font_url>[a-zA-Z0-9_\-\\\/\.]+\.(ttf|svg|woff|eot)) \*/"
