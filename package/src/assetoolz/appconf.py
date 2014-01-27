import os
import json


class AppConfHelper(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(AppConfHelper, cls).__new__(cls)
            cls.instance._appconf_path = None
            cls.instance._appconf = None
        return cls.instance

    def initialize(self, path):
        self._appconf_path = path

    def _depth_process(self, obj, path):
        result = obj
        keys = result.keys()
        for key in keys:
            #print('KEY %s' % key)
            if key == '__include':
                include_path = result['__include']
                print('INCLUDE %s' % include_path)
                full_path = os.path.join(os.path.dirname(path), include_path)
                result.update(self._parse_appconf_internal(full_path))
            else:
                next = result[key]
                if isinstance(next, dict):
                    next = self._depth_process(next, path)
        return result

    def _parse_appconf_internal(self, path):
        obj = None
        with open(path, 'r') as f:
            obj = json.load(f)
        obj = self._depth_process(obj, path)
        return obj

    def parse_appconf(self):
        if self._appconf is None:
            self._appconf = self._parse_appconf_internal(os.path.join(
                self._appconf_path, 'index.json'))

    def find_replacement(self, key):
        self.parse_appconf()
        parts = key.split('.')
        #print(parts)

        obj = self._appconf
        for x in range(0, len(parts)):
            part = parts[x]
            if part in obj:
                if x < len(parts):
                    obj = obj[part]
            else:
                obj = 'NLKF'
                break

        return obj