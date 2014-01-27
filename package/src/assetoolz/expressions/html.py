from __future__ import absolute_import
from . import BaseExpression, BaseIncludeExpression
import os
import cgi
from utils import load_file


class IncludeExpression(BaseIncludeExpression):
    def __init__(self, asset, match):
        super(IncludeExpression, self).__init__(asset, match,
                                                "html", "_%s.html")

    @staticmethod
    def get_regex():
        return r"\[\%= include \"(?P<p_include_path>[a-zA-Z0-9_\-]+)\" \%\]"


class IncludeHtmlEscapeExpression(BaseIncludeExpression):
    def __init__(self, asset, match):
        super(IncludeHtmlEscapeExpression, self).__init__(
            asset, match, "html", "_%s.html", "p_include_path2")

    @staticmethod
    def get_regex_params():
        return ["p_include_path2"]

    @staticmethod
    def get_regex():
        return r"\[\%= include_html_escape \"(?P<p_include_path2>[a-zA-Z0-9_\-]+)\" \%\]"

    def __call__(self, **opts):
        cache_entry = self.asset._tool_cache.find_entry(self._dependency_path)
        if cache_entry:
            return cgi.escape(load_file(cache_entry.target), True)
        return ""


class LinkExpression(BaseExpression):
    def __init__(self, asset, match):
        super(LinkExpression, self).__init__(asset, match)
        self._link_path = match.group("p_stylesheet_link_href")
        self._dependency_path = os.path.join(self.asset._settings.assets,
                                             "stylesheets",
                                             self._link_path)
        self.asset.add_dependency(self._dependency_path)

    def __call__(self, *args, **opts):
        cache_entry = self.asset._tool_cache.find_entry(self._dependency_path)
        if cache_entry:
            return '<link href="%s" media="all" rel="stylesheet" />' %\
                os.path.relpath(cache_entry.target, os.path.dirname(opts["path"]))
        return ""

    @staticmethod
    def get_regex_params():
        return ["p_stylesheet_link_href"]

    @staticmethod
    def get_regex():
        return r"\[\%= stylesheet_link_tag \"(?P<p_stylesheet_link_href>[a-zA-Z0-9_\-]+\.css)\" \%\]"


class RequirejsIncludeExpression(BaseExpression):
    def __init__(self, asset, match):
        super(RequirejsIncludeExpression, self).__init__(asset, match)
        self._requirejs_lib = match.group("p_requirejs_lib")
        self._requirejs_main = match.group("p_requirejs_main")
        self._dependency_path1 = os.path.join(self.asset._settings.assets,
                                              "scripts",
                                              self._requirejs_lib)
        self._dependency_path2 = os.path.join(self.asset._settings.assets,
                                              "scripts",
                                              self._requirejs_main)
        self.asset.add_dependency(self._dependency_path1)
        self.asset.add_dependency(self._dependency_path2)

    def __call__(self, *args, **opts):
        cache_entry1 = self.asset._tool_cache.find_entry(self._dependency_path1)
        cache_entry2 = self.asset._tool_cache.find_entry(self._dependency_path2)
        if cache_entry1 and cache_entry2:
            return '<script src="%s" data-main="%s"></script>' %\
                (os.path.relpath(cache_entry1.target, os.path.dirname(opts["path"])),
                 os.path.relpath(cache_entry2.target, os.path.dirname(opts["path"])))
        return ""

    @staticmethod
    def get_regex_params():
        return ["p_requirejs_lib", "p_requirejs_main"]

    @staticmethod
    def get_regex():
        return r"\[\%= requirejs_include_tag \"(?P<p_requirejs_lib>[a-zA-Z0-9_\-]+\.js)\", \"(?P<p_requirejs_main>[a-zA-Z0-9_\-]+\.js)\" \%\]"


class ImageExpression(BaseExpression):
    def __init__(self, asset, match):
        super(ImageExpression, self).__init__(asset, match)
        self._image_href = match.group("p_image_href")
        self._dependency_path = os.path.join(self.asset._settings.assets,
                                             "images",
                                             self._image_href)
        self.asset.add_dependency(self._dependency_path)

    def __call__(self, *args, **opts):
        cache_entry = self.asset._tool_cache.find_entry(self._dependency_path)
        if cache_entry:
            path = os.path.relpath(cache_entry.target,
                                   os.path.dirname(opts["path"]))
            alt = os.path.splitext(os.path.basename(cache_entry.source))[0]
            return '<image src="%s" alt="%s" />' % (path, alt)
        return ""

    @staticmethod
    def get_regex_params():
        return ["p_image_href"]

    @staticmethod
    def get_regex():
        return r"\[\%= image_tag \"(?P<p_image_href>[a-zA-Z0-9_\-]+\.(png|jpg|gif))\" \%\]"