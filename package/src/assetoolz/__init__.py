from __future__ import absolute_import
import argparse
import os
from assetoolz.detour import detour_directory
from assetoolz.cache import Cache
from assetoolz.db import entry_point
from assetoolz.i18n import LocalizationHelper
from assetoolz.appconf import AppConfHelper
from assetoolz.assets import AssetCollection
import yaml
from assetoolz.utils import load_file
from assetoolz.i18n_alt import I18nHelper


class AssetSettings:
    def __init__(self, data):
        self._data = data

    @property
    def source(self):
        return self._data['source']

    @property
    def target(self):
        return self._data['target']

    @property
    def languages(self):
        return None


class LocalizedAssetSettings(AssetSettings):
    @property
    def languages(self):
        return self._data['languages']


class Settings:
    def __init__(self, conf_file):
        self._data = yaml.load(load_file(conf_file))
        self._html = LocalizedAssetSettings(self._data['html'])
        self._images = AssetSettings(self._data['images'])
        self._scripts = AssetSettings(self._data['scripts'])
        self._stylesheets = AssetSettings(self._data['stylesheets'])

        self._i18n_helper = I18nHelper(self._data['i18n_alt'])

    @property
    def cdn_path(self):
        return self._data['cdn']['path']

    @property
    def cdn_url(self):
        return self._data['cdn']['url']

    @property
    def force(self):
        return self._data['force'] if 'force' in self._data else False

    @property
    def minify(self):
        return self._data['minify']

    @property
    def yuicompressor_file(self):
        return self._data['yuicompressor_file']

    @property
    def htmlcompressor_file(self):
        return self._data['htmlcompressor_file']

    @property
    def appconf(self):
        return self._data['config']

    @property
    def i18n(self):
        return self._data['i18n']

    @property
    def cache_path(self):
        return self._data['cache']

    @property
    def partials(self):
        return os.path.join(self.cache_path, "partials")

    @property
    def html(self):
        return self._html

    @property
    def images(self):
        return self._images

    @property
    def scripts(self):
        return self._scripts

    @property
    def stylesheets(self):
        return self._stylesheets

    @property
    def i18n_helper(self):
        return self._i18n_helper


@entry_point
def compile(settings):
    file_list = []
    update_file_list = lambda x: file_list.append(x)

    detour_directory(settings.html.source, update_file_list)
    detour_directory(settings.scripts.source, update_file_list)
    detour_directory(settings.stylesheets.source, update_file_list)
    detour_directory(settings.images.source, update_file_list)

    tool_cache = Cache()
    tool_cache.check()

    assets = AssetCollection(file_list, settings)
    assets.pick_dependencies()
    assets.build()


def main(**opts):
    parser = argparse.ArgumentParser(description="assetoolz")
    parser.add_argument("--config", metavar="config",
                        type=str)

    args = parser.parse_args()
    config = args.config if args.config else opts["config"]
    settings = Settings(config)
    LocalizationHelper().initialize(settings.i18n)
    AppConfHelper().initialize(settings.appconf)
    compile(settings)

if __name__ == "__main__":
    main(config="C:\\Work\\community\\assetoolz\\test_data\\assets\\config.yml")
