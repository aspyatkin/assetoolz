

class ResourceSet(object):
    def __init__(self, settings):
        self.resources = self.parse_resource('', '', settings)

    @classmethod
    def urljoin(cls, *args):
        if len(args) > 0 and len(args[0]) == 0:
            args = args[1:]
        return '/'.join(map(lambda x: x.rstrip('/'), args))

    @classmethod
    def parse_resource(cls, base_alias, base_url, settings):
        result = {}
        resource_base = cls.urljoin(base_url, settings['base_url'])
        for alias, value in settings['resources'].iteritems():
            cur_base = cls.urljoin(base_alias, alias)
            if type(value) == dict:
                result.update(cls.parse_resource(
                    cur_base, resource_base, value))
            else:
                result[cur_base] = cls.urljoin(resource_base, value)

        return result

    def __repr__(self):
        r = 'RESOURCES:\r\n'
        for alias, url in self.resources.iteritems():
            r += '{alias}\t{url}\r\n'.format(alias=alias, url=url)
        return r

    def get_url(self, alias):
        if alias in self.resources:
            return self.resources[alias]
        return '#'
