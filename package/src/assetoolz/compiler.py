import re
import codecs
import os
from i18n import LocalizationHelper
from appconf import AppConfHelper
import cgi
from cache import Cache
from expressions import ExpressionSettings


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


class VariableBase(object):
    def __init__(self, value, varholder):
        self._value = self._parse(value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if type(value) == type(self._value):
            self._value = value

    def __repr__(self):
        return repr(self._value)


class ExpressionEval(object):
    def __init__(self, expr_str, varholder):
        self._varholder = varholder
        self._expr = self._parse(expr_str)

    def get_result():
        return None


class CastBooleanExpressionEval(ExpressionEval):
    def _parse(self, expr_str):
        self._variable = self._varholder.find_variable(expr_str)

    def get_result(self):
        if self._variable is None:
            return None
        return bool(self._variable._value)

    @staticmethod
    def get_regex():
        return r"^[a-zA-Z0-9_]+$"


class EqualExpressionEval(ExpressionEval):
    def _parse(self, expr_str):
        print("I m here")
        match = re.match(self.get_regex(), expr_str)
        self._var_1 = self._varholder.get_variable_obj(match.group("var1"))
        self._var_2 = self._varholder.get_variable_obj(match.group("var2"))

    def get_result(self):
        print("Var 1 is '%s'" % self._var_1._value)
        print("Var 2 is '%s'" % self._var_2._value)
        if self._var_1._value is None or self._var_2._value is None:
            return None
        return self._var_1._value == self._var_2._value

    @staticmethod
    def get_regex():
        return r"^(?P<var1>([0-9]+|\".+\"|true|false|[a-zA-Z0-9_]+)) == (?P<var2>([0-9]+|\".+\"|true|false|[a-zA-Z0-9_]+))$"


class VariableNumber(VariableBase):
    def _parse(self, value):
        return int(value)

    @staticmethod
    def get_regex():
        return r"^[0-9]+$"


class VariableBoolean(VariableBase):
    def _parse(self, value):
        return value == "true"

    @staticmethod
    def get_regex():
        return r"^(true|false)$"


class VariableString(VariableBase):
    def _parse(self, value):
        regex = self.get_regex()
        match = re.match(regex, value)
        if match:
            return match.group("val")
        return ""

    @staticmethod
    def get_regex():
        return r"^\"(?P<val>.+)\"$"


class DeclaredVariable(VariableBase):
    def __init__(self, value, varholder):
        variable = varholder.find_variable(value)
        self._value = variable._value if variable else None
        self._varholder = varholder

    @staticmethod
    def get_regex():
        return r"^[a-zA-Z0-9_]+$"


class VariablesHolder(object):
    def __init__(self):
        self._variables = {}

    def add_variable(self, name, value_str):
        variable = self.get_variable_obj(value_str)
        assert(variable)
        self._variables[name] = variable

    def find_variable(self, name):
        if not name in self._variables:
            return None
        return self._variables[name]

    @staticmethod
    def supported_variables():
        return [VariableBoolean,
                VariableNumber,
                VariableString,
                DeclaredVariable]

    def get_variable_obj(self, value_str):
        for class_name in self.supported_variables():
            match = re.match(class_name.get_regex(), value_str)
            if match is not None:
                return class_name(value_str, self)
        return None

    @staticmethod
    def supported_expressions():
        return [CastBooleanExpressionEval,
                EqualExpressionEval]

    def get_variable_expression(self, expr_str):
        for class_name in self.supported_expressions():
            match = re.match(class_name.get_regex(), expr_str)
            if match is not None:
                return class_name(expr_str, self)
        return None


class ExpressionProcessor(object):
    def __init__(self, asset, resolvers):
        self._asset = asset
        self._data = asset._data
        self._resolvers = resolvers
        self._expressions = []
        self._varholder = VariablesHolder()

    def parse(self):
        group_regex = get_expressions_regex(self._resolvers)
        for match in re.finditer(group_regex, self._data):
            class_name = get_match_expression_class(
                match, self._resolvers)

            if class_name is not None:
                #print(str(class_name))
                expr = class_name(ExpressionSettings(
                    self, self._asset, match))
                self._expressions.append(expr)

        print(str(self._expressions))
        print(str(self._varholder._variables))

    def compile(self, settings, path):
        result = ''
        start = 0
        end = len(self._data)
        last_expression = None
        for expression in self._expressions:
            if last_expression:
                expression._php_stub = last_expression._php_stub
                expression._conditional = last_expression._conditional
                expression._skip_block = last_expression._skip_block

            span = expression.settings.match.span()
            end = span[0]
            if expression._conditional and expression._skip_block:
                print("Skip block")
            else:
                result += self._data[start:end]
            expr_result = expression(settings=settings, path=path)
            if expression._conditional and expression._skip_block:
                print("Skip block next")
            else:
                result += expr_result
            start = span[1]
            end = len(self._data)
            last_expression = expression

        result += self._data[start:end]
        self._asset._data = result
