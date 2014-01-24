import re
import codecs
import os
from i18n import LocalizationHelper
from appconf import AppConfHelper
import cgi


def load_file(path):
    data = None
    with codecs.open(path, "r", "utf_8") as f:
        data = f.read()
    return data


def save_file(path, data):
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with codecs.open(path, "w", "utf_8") as f:
        f.write(data)


class Expression(object):
    def __init__(self, *args, **opts):
        pass

    def __call__(self, *args, **opts):
        return None


class AppConfExpression(Expression):
    def __init__(self, match_obj, *args, **opts):
        self.key = match_obj.group("p_appconf_key")

    def __call__(self, *args, **opts):
        return repr(AppConfHelper().find_replacement(self.key))

    @staticmethod
    def get_regex_params():
        return ["p_appconf_key"]

    @staticmethod
    def get_regex():
        return r"\[\%= config \"(?P<p_appconf_key>[a-zA-Z0-9 ]{2,48}(\.[a-zA-Z0-9 ]{2,48})*)\" \%\]"


class I18nExpression(Expression):
    def __init__(self, match_obj, *args, **opts):
        self.key = match_obj.group("p_i18n_key")

    def __call__(self, *args, **opts):
        return LocalizationHelper().find_replacement(self.key, "en")

    @staticmethod
    def get_regex_params():
        return ["p_i18n_key"]

    @staticmethod
    def get_regex():
        return r"\[ (?P<p_i18n_key>[a-zA-Z0-9 ]{2,48}(\|[a-zA-Z0-9 ]{2,48})*) \]"


class StylesheetLinkTagExpression(Expression):
    def __init__(self, match_obj, *args, **opts):
        self.link_path = match_obj.group("p_stylesheet_link_href")

    def __call__(self, *args, **opts):
        return '<link href="%s" media="all" rel="stylesheet" />' % self.link_path

    @staticmethod
    def get_regex_params():
        return ["p_stylesheet_link_href"]

    @staticmethod
    def get_regex():
        return r"\[\%= stylesheet_link_tag \"(?P<p_stylesheet_link_href>[a-zA-Z0-9_\-\.]+)\" \%\]"


class IncludeExpression(Expression):
    def __init__(self, match_obj, *args, **opts):
        self.include_path = match_obj.group("p_include")
        self._settings = opts["settings"]
        self._path = opts["path"]

    def __call__(self, *args, **opts):
        common_prefix = os.path.commonprefix([self._path, self._settings.assets])
        dir_part = os.path.dirname(self._path[len(common_prefix)+1:])
        include_dir = os.path.dirname(self.include_path)
        include_file = "_%s%s" % (os.path.basename(self.include_path),
                                   os.path.splitext(self._path)[1])
        partials_path = os.path.join(self._settings.partials, dir_part,
                                     os.path.join(include_dir, include_file))
        print str("Including from %s" % partials_path)
        return load_file(partials_path)

    @staticmethod
    def get_regex_params():
        return ["p_include"]

    @staticmethod
    def get_regex():
        return r"\[\%= include \"(?P<p_include>[a-zA-Z0-9_\-]+)\" \%\]"


class IncludeHtmlEscapeExpression(IncludeExpression):
    def __init__(self, match_obj, *args, **opts):
        self.include_path = match_obj.group("p_include_html_escape")
        self._settings = opts["settings"]
        self._path = opts["path"]

    def __call__(self, *args, **opts):
        raw = super(IncludeHtmlEscapeExpression, self).__call__(self, *args, **opts)
        return cgi.escape(raw, True)

    @staticmethod
    def get_regex_params():
        return ["p_include_html_escape"]

    @staticmethod
    def get_regex():
        return r"\[\%= include_html_escape \"(?P<p_include_html_escape>[a-zA-Z0-9_\-]+)\" \%\]"


class ExpressionResolver(object):
    def __init__(self, expression_classes, settings, path):
        self.expression_classes = expression_classes
        self.expressions = []
        self._settings = settings
        self._path = path

    def __call__(self, match_obj):
        class_name = get_match_expression_class(
            match_obj, self.expression_classes)

        if class_name is not None:
            print(str(class_name))
            expr = class_name(match_obj, settings=self._settings,
                              path=self._path)
            self.expressions.append(expr)
            return expr()
        return ''


def get_match_expression_class(match_obj, classes):
    for class_name in classes:
        matches = True
        for param in class_name.get_regex_params():
            if match_obj.group(param) is None:
                matches = False
                break
        if matches:
            return class_name
    return None


def get_expressions_regex(classes):
    grouped = ["(%s)" % x.get_regex() for x in classes]
    return "|".join(grouped)


def process(path, settings):
    data = load_file(path)
    expression_classes = [IncludeExpression,
                          StylesheetLinkTagExpression,
                          I18nExpression,
                          AppConfExpression,
                          IncludeHtmlEscapeExpression]
    processor = ExpressionResolver(expression_classes, settings, path)

    new_data = re.sub(get_expressions_regex(expression_classes),
                      processor, data)
    print(str(processor.expressions))
    common_prefix = os.path.commonprefix([path, settings.assets])
    filename_part = path[len(common_prefix)+1:]
    if os.path.basename(path).startswith("_"):
        target_path = os.path.join(settings.partials, filename_part)
    else:
        target_path = os.path.join(settings.output, filename_part)
    print("Filename path is %s" % filename_part)
    print("Output path is %s" % settings.output)
    save_file(target_path, new_data)
