import re
import os
import json
import io


class LocalizationHelper(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(LocalizationHelper, cls).__new__(cls)
            cls.instance._locales_path = None
            cls.instance._locales = None
        return cls.instance

    def initialize(self, path):
        self._locales_path = path

    def _depth_process(self, obj, path):
        result = obj
        keys = result.keys()
        for key in keys:
            #print('KEY %s' % key)
            if key == '__include':
                include_path = result['__include']
                #print('INCLUDE %s' % include_path)
                full_path = os.path.join(os.path.dirname(path), include_path)
                result.update(self._parse_locale_file_internal(full_path))
            else:
                next = result[key]
                if isinstance(next, dict):
                    next = self._depth_process(next, path)
        return result

    def _parse_locale_file_internal(self, path):
        obj = None
        with io.open(path, 'rb') as f:
            obj = json.load(f)
        obj = self._depth_process(obj, path)
        return obj

    def _parse_locales(self):
        if self._locales is None:
            self._locales = self._parse_locale_file_internal(os.path.join(
                self._locales_path, 'index.json'))

    class InlineReplacer(object):
        def __init__(self, params):
            self._params = params

        def __call__(self, match_obj):
            return self._params[int(match_obj.group(0)[1:-1])]

    def build_string(self, source, params, lang):
        if params is None:
            return source
        else:
            target = re.sub(r'\{[0-9]{1,2}\}',
                            LocalizationHelper.InlineReplacer(params), source)
            return self.localize_data(target, lang)

    def find_replacement(self, key, lang):
        self._parse_locales()
        parts = key.split('|')
        #print(parts)

        obj = self._locales
        for x in range(0, len(parts)):
            part = parts[x]
            if part in obj:
                if x < len(parts) - 1:
                    obj = obj[part]
                else:
                    lang_key = '__%s' % lang
                    alias_key = '__alias'
                    default_key = '__default'
                    template_params = None

                    if '__params' in obj[part]:
                        template_params = obj[part]['__params']

                    if alias_key in obj[part]:
                        obj = self.find_replacement(obj[part][alias_key], lang)
                    elif lang_key in obj[part]:
                        obj = self.build_string(obj[part][lang_key],
                                                template_params, lang)
                    elif default_key in obj[part]:
                        obj = self.build_string(obj[part][default_key],
                                                template_params, lang)
                    else:
                        obj = 'NLVF'
            else:
                obj = 'NLKF'
                break

        return obj

    class Replacer(object):
        def __init__(self, helper, lang):
            self._lang = lang
            self._helper = helper

        def __call__(self, match_obj):
            token = match_obj.group(0)[2:-2]
            return self._helper.find_replacement(token, self._lang)

    def localize_data(self, data, lang):
        return re.sub(
            r'\[ [a-zA-Z0-9 ]{2,28}(\|[a-zA-Z0-9 ]{2,28})* \]',
            LocalizationHelper.Replacer(self, lang), data)
