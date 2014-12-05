class AppConfHelper(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(AppConfHelper, cls).__new__(cls)
            cls.instance._appconf = None
        return cls.instance

    def initialize(self, config):
        self._appconf = config

    def find_replacement(self, key):
        parts = key.split(':')

        obj = self._appconf
        for x in range(0, len(parts)):
            part = parts[x]
            if part in obj:
                if x < len(parts):
                    obj = obj[part]
            else:
                obj = 'missing key {0}'.format(key)
                break

        return obj
