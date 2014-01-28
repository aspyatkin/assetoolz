from __future__ import absolute_import
from . import BaseExpression, BaseIncludeExpression
import os
from cache import Cache


class IncludeExpression(BaseIncludeExpression):
    def __init__(self, settings):
        super(IncludeExpression, self).__init__(settings,
                                                "stylesheets", "_%s")

    @staticmethod
    def get_regex():
        return r"/\*= include (?P<p_include_path>[a-zA-Z0-9_\-]+\.(css|scss|sass)) \*/"


class ImagePathExpression(BaseExpression):
    def __init__(self, settings):
        super(ImagePathExpression, self).__init__(settings)
        self._image_path = settings.match.group("p_image_path")
        self._dependency_path = os.path.join(settings.asset._settings.assets,
                                             "images",
                                             self._image_path)
        settings.asset.add_dependency(self._dependency_path)

    def __call__(self, **opts):
        tool_cache = Cache()
        cache_entry = tool_cache.find_entry(self._dependency_path)
        if cache_entry is None:
            print("Not found %s" % self._image_path)
            return ''
        else:
            return os.path.relpath(cache_entry.target, os.path.dirname(opts["path"]))

    @staticmethod
    def get_regex_params():
        return ["p_image_path"]

    @staticmethod
    def get_regex():
        return r"\[\%= image_path \"(?P<p_image_path>[a-zA-Z0-9_\-]+\.(png|gif|jpg))\" \%\]"