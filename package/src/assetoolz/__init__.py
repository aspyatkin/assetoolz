from __future__ import absolute_import
import argparse
import os
from detour import detour_directory
from cache import Cache
from db import entry_point
from i18n import LocalizationHelper
from appconf import AppConfHelper
from assets import AssetCollection


class Settings:
    def __init__(self, appconf, assets, output):
        self._appconf = appconf
        self._assets = assets
        self._output = output

    @property
    def appconf(self):
        return self._appconf

    @property
    def assets(self):
        return self._assets

    @property
    def output(self):
        return self._output

    @property
    def i18n(self):
        return os.path.join(self._assets, "i18n")

    @property
    def partials(self):
        return os.path.join(self._assets, "build", "partials")


@entry_point
def compile(settings):
    file_list = []
    html_path = os.path.join(settings.assets, "html")
    script_path = os.path.join(settings.assets, "scripts")
    stylesheet_path = os.path.join(settings.assets, "stylesheets")
    image_path = os.path.join(settings.assets, "images")
    update_file_list = lambda x: file_list.append(x)

    detour_directory(html_path, update_file_list)
    detour_directory(script_path, update_file_list)
    detour_directory(stylesheet_path, update_file_list)
    detour_directory(image_path, update_file_list)

    tool_cache = Cache()
    tool_cache.check()

    assets = AssetCollection(file_list, settings)
    assets.pick_dependencies()
    assets.build()


def main(**opts):
    parser = argparse.ArgumentParser(description="assetoolz")
    parser.add_argument("--appconf", metavar="appconf",
                        type=str)
    parser.add_argument("--assets", metavar="assets",
                        type=str)
    parser.add_argument("--output", metavar="output",
                        type=str)
    args = parser.parse_args()
    appconf = args.appconf if args.appconf else opts["appconf"]
    assets = args.assets if args.assets else opts["assets"]
    output = args.output if args.output else opts["output"]
    settings = Settings(appconf, assets, output)
    LocalizationHelper().initialize(settings.i18n)
    AppConfHelper().initialize(settings.appconf)
    compile(settings)

if __name__ == "__main__":
    main(appconf="C:\\Work\\community\\assetoolz\\test_data\\appconf",
         assets="C:\\Work\\community\\assetoolz\\test_data\\assets",
         output="C:\\Work\\community\\assetoolz\\test_data\\results\\www")
