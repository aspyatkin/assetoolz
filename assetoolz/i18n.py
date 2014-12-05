import io
import yaml
from xml.sax.saxutils import escape


def escape_html(text):
    html_escape_table = {'"': "&quot;", "'": "&apos;"}
    return escape(text, html_escape_table)


class I18nHelper(object):
    def __init__(self, data):
        self.translations = {}
        for lang, file_path in data.iteritems():
            self.load_translation(lang, file_path)

    def load_translation(self, lang, file_path):
        with io.open(file_path, 'r', encoding='utf8') as f:
            self.translations[lang] = yaml.load(f)

    def translate(self, key, lang):
        parts = key.split(':')

        obj = None
        if not lang in self.translations:
            obj = self.translations['en']
        else:
            obj = self.translations[lang]

        for x in range(0, len(parts)):
            part = parts[x]
            if part in obj:
                obj = obj[part]
            else:
                obj = '{0}, {1}'.format(lang, key)
                break

        if key.endswith('_html'):
            return obj
        return escape_html(obj)
