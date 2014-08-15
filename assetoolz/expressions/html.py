from . import BaseExpression, BaseIncludeExpression
import os
import json
from ..appconf import AppConfHelper
from ..utils import make_url_path


class IncludeExpression(BaseIncludeExpression):
    def __init__(self, settings):
        super(IncludeExpression, self).__init__(
            settings,
            settings.asset._settings.html.source,
            "_%s.html")

    @staticmethod
    def get_regex():
        return r"\[\%= include (?P<p_include_path>[a-zA-Z0-9_\-\\\/\.]+) \%\]"


class I18nExpression(BaseExpression):
    def __init__(self, settings):
        super(I18nExpression, self).__init__(settings)
        self._key = settings.match.group('p_i18n_key')

    def __call__(self, *args, **opts):
        return self.settings.asset._settings.i18n_helper.translate(self._key, self.settings.asset._lang)

    @staticmethod
    def get_regex_params():
        return ['p_i18n_key']

    @staticmethod
    def get_regex():
        return r"\[\%\- (?P<p_i18n_key>[a-zA-Z0-9_ \-]{1,50}(\:[a-zA-Z0-9_ \-]{1,50})*) \%\]"


class AppConfExpression(BaseExpression):
    def __init__(self, settings):
        super(AppConfExpression, self).__init__(settings)
        self._key = settings.match.group('p_appconf_key')
        self._filter = settings.match.group('p_appconf_filter')

    def __call__(self, *args, **opts):
        base = AppConfHelper().find_replacement(self._key)
        if self._filter == '':
            return str(base)
        elif self._filter == 'json':
            return json.dumps(base)
        else:
            return ''

    @staticmethod
    def get_regex_params():
        return ['p_appconf_key', 'p_appconf_filter']

    @staticmethod
    def get_regex():
        return r"\[\!(?P<p_appconf_key>[a-zA-Z0-9_\- ]{2,48}(\|[a-zA-Z0-9_\- ]{2,48})*)\!(?P<p_appconf_filter>[a-zA-Z0-9_\- ]{0,25})\]"


class StylesheetUrlExpression(BaseExpression):
    def __init__(self, settings):
        super(StylesheetUrlExpression, self).__init__(settings)
        self._link_path = settings.match.group("p_stylesheet_url")
        self._dependency_path = os.path.join(
            self.settings.asset._settings.stylesheets.source,
            self._link_path)
        settings.asset.add_dependency(self._dependency_path)

    def __call__(self, *args, **opts):
        cache_entry = self.settings.asset._tool_cache.find_entry(
            self._dependency_path)
        if cache_entry:
            return make_url_path(
                self.settings.asset._settings.cdn_path,
                self.settings.asset._settings.cdn_url,
                cache_entry.target
            )
        return ""

    @staticmethod
    def get_regex_params():
        return ["p_stylesheet_url"]

    @staticmethod
    def get_regex():
        return r"\[\%= stylesheet_url (?P<p_stylesheet_url>[a-zA-Z0-9_\-\\\/\.]+\.(css|sass|scss)) \%\]"


class ScriptUrlExpression(BaseExpression):
    def __init__(self, settings):
        super(ScriptUrlExpression, self).__init__(settings)
        self._link_path = settings.match.group("p_script_url")
        self._dependency_path = os.path.join(
            self.settings.asset._settings.scripts.source,
            self._link_path)
        settings.asset.add_dependency(self._dependency_path)

    def __call__(self, *args, **opts):
        cache_entry = self.settings.asset._tool_cache.find_entry(self._dependency_path)
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
        return r"\[\%= script_url (?P<p_script_url>[a-zA-Z0-9_\-\\\/\.]+\.(js|coffee)) \%\]"


class ImageUrlExpression(BaseExpression):
    def __init__(self, settings):
        super(ImageUrlExpression, self).__init__(settings)
        self._image_href = settings.match.group("p_image_href")
        self._dependency_path = os.path.join(
            self.settings.asset._settings.images.source,
            self._image_href)
        settings.asset.add_dependency(self._dependency_path)

    def __call__(self, *args, **opts):
        cache_entry = self.settings.asset._tool_cache.find_entry(self._dependency_path)
        if cache_entry:
            return make_url_path(
                self.settings.asset._settings.cdn_path,
                self.settings.asset._settings.cdn_url,
                cache_entry.target
            )
        return ""

    @staticmethod
    def get_regex_params():
        return ["p_image_href"]

    @staticmethod
    def get_regex():
        return r"\[\%= image_url (?P<p_image_href>[a-zA-Z0-9_\-\\\/\.]+\.(png|jpg|gif)) \%\]"


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
        return r'\[\%= resource_url (?P<p_resource_url>[a-zA-Z0-9_\-]+((/[a-zA-Z0-9_\-]+)*)) \%\]'
