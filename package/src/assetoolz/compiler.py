import re
import codecs
import os
from assetoolz.expressions import ExpressionSettings


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


class ExpressionProcessor(object):
    def __init__(self, asset, resolvers):
        self._asset = asset
        self._data = asset._data
        self._resolvers = resolvers
        self._expressions = []

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

        #print(str(self._expressions))

    def compile(self, settings, path):
        result = ''
        start = 0
        end = len(self._data)
        for expression in self._expressions:
            span = expression.settings.match.span()
            end = span[0]

            result += self._data[start:end]
            expr_result = expression(settings=settings, path=path)

            result += expr_result
            start = span[1]
            end = len(self._data)

        result += self._data[start:end]
        self._asset._data = result
