from __future__ import absolute_import
from . import BaseExpression, BaseIncludeExpression
import os
import cgi
from utils import load_file


class IncludeExpression(BaseIncludeExpression):
    def __init__(self, settings):
        super(IncludeExpression, self).__init__(settings,
                                                "html", "_%s.html")

    @staticmethod
    def get_regex():
        return r"\[\%= include \"(?P<p_include_path>[a-zA-Z0-9_\-]+)\" \%\]"


class IncludeHtmlEscapeExpression(BaseIncludeExpression):
    def __init__(self, settings):
        super(IncludeHtmlEscapeExpression, self).__init__(
            settings, "html", "_%s.html", "p_include_path2")

    @staticmethod
    def get_regex_params():
        return ["p_include_path2"]

    @staticmethod
    def get_regex():
        return r"\[\%= include_html_escape \"(?P<p_include_path2>[a-zA-Z0-9_\-]+)\" \%\]"

    def __call__(self, **opts):
        cache_entry = self.settings.asset._tool_cache.find_entry(self._dependency_path)
        if cache_entry:
            return cgi.escape(load_file(cache_entry.target), True)
        return ""


class LinkExpression(BaseExpression):
    def __init__(self, settings):
        super(LinkExpression, self).__init__(settings)
        self._link_path = settings.match.group("p_stylesheet_link_href")
        self._dependency_path = os.path.join(self.settings.asset._settings.assets,
                                             "stylesheets",
                                             self._link_path)
        settings.asset.add_dependency(self._dependency_path)

    def __call__(self, *args, **opts):
        cache_entry = self.settings.asset._tool_cache.find_entry(self._dependency_path)
        if cache_entry:
            return '<link href="%s" media="all" rel="stylesheet" />' %\
                os.path.relpath(cache_entry.target, os.path.dirname(opts["path"]))
        return ""

    @staticmethod
    def get_regex_params():
        return ["p_stylesheet_link_href"]

    @staticmethod
    def get_regex():
        return r"\[\%= stylesheet_link_tag \"(?P<p_stylesheet_link_href>[a-zA-Z0-9_\-]+\.css)\" \%\]"


class RequirejsIncludeExpression(BaseExpression):
    def __init__(self, settings):
        super(RequirejsIncludeExpression, self).__init__(settings)
        self._requirejs_lib = settings.match.group("p_requirejs_lib")
        self._requirejs_main = settings.match.group("p_requirejs_main")
        self._dependency_path1 = os.path.join(self.settings.asset._settings.assets,
                                              "scripts",
                                              self._requirejs_lib)
        self._dependency_path2 = os.path.join(self.settings.asset._settings.assets,
                                              "scripts",
                                              self._requirejs_main)
        settings.asset.add_dependency(self._dependency_path1)
        settings.asset.add_dependency(self._dependency_path2)

    def __call__(self, *args, **opts):
        cache_entry1 = self.settings.asset._tool_cache.find_entry(self._dependency_path1)
        cache_entry2 = self.settings.asset._tool_cache.find_entry(self._dependency_path2)
        if cache_entry1 and cache_entry2:
            return '<script src="%s" data-main="%s"></script>' %\
                (os.path.relpath(cache_entry1.target, os.path.dirname(opts["path"])),
                 os.path.relpath(cache_entry2.target, os.path.dirname(opts["path"])))
        return ""

    @staticmethod
    def get_regex_params():
        return ["p_requirejs_lib", "p_requirejs_main"]

    @staticmethod
    def get_regex():
        return r"\[\%= requirejs_include_tag \"(?P<p_requirejs_lib>[a-zA-Z0-9_\-]+\.js)\", \"(?P<p_requirejs_main>[a-zA-Z0-9_\-]+\.js)\" \%\]"


class ImageExpression(BaseExpression):
    def __init__(self, settings):
        super(ImageExpression, self).__init__(settings)
        self._image_href = settings.match.group("p_image_href")
        self._dependency_path = os.path.join(self.settings.asset._settings.assets,
                                             "images",
                                             self._image_href)
        settings.asset.add_dependency(self._dependency_path)

    def __call__(self, *args, **opts):
        cache_entry = self.settings.asset._tool_cache.find_entry(self._dependency_path)
        if cache_entry:
            path = os.path.relpath(cache_entry.target,
                                   os.path.dirname(opts["path"]))
            alt = os.path.splitext(os.path.basename(cache_entry.source))[0]
            return '<image src="%s" alt="%s" />' % (path, alt)
        return ""

    @staticmethod
    def get_regex_params():
        return ["p_image_href"]

    @staticmethod
    def get_regex():
        return r"\[\%= image_tag \"(?P<p_image_href>[a-zA-Z0-9_\-]+\.(png|jpg|gif))\" \%\]"


class VariableDeclareExpression(BaseExpression):
    def __init__(self, settings):
        super(VariableDeclareExpression, self).__init__(settings)
        self._variable_name = settings.match.group("p_var_name")
        self._variable_value = settings.match.group("p_var_value")

    def __call__(self, *args, **opts):
        self.settings.processor._varholder.add_variable(
            self._variable_name,
            self._variable_value)
        return ""

    @staticmethod
    def get_regex_params():
        return ["p_var_name", "p_var_value"]

    @staticmethod
    def get_regex():
        return r"\[\% (?P<p_var_name>[A-Za-z0-9_]+) = (?P<p_var_value>(true|false|\".+\"|[0-9]+|[A-Za-z0-9_]+)) \%\]"


class VariableDisplayExpression(BaseExpression):
    def __init__(self, settings):
        super(VariableDisplayExpression, self).__init__(settings)
        self._variable_name = settings.match.group("p_var_name_display")

    def __call__(self, *args, **opts):
        variable = self.settings.processor._varholder.find_variable(self._variable_name)
        if variable is not None:
            return str(variable)
        return "<?php echo($%s); ?>" % self._variable_name

    @staticmethod
    def get_regex_params():
        return ["p_var_name_display"]

    @staticmethod
    def get_regex():
        return r"\[\%= (?P<p_var_name_display>[a-zA-Z0-9_]+) \%\]"


class UnaryConditionalWhenExpression(BaseExpression):
    def __init__(self, settings):
        super(UnaryConditionalWhenExpression, self).__init__(settings)
        self._variable_str = settings.match.group("p_var_unary_cond")

    def __call__(self, *args, **opts):
        expression = self.settings.processor._varholder.get_variable_expression(self._variable_str)
        self._php_stub = False
        self._conditional = True
        expr_result = None
        if expression:
            expr_result = expression.get_result()
            if expr_result is None:
                self._php_stub = True
            else:
                print(str(expr_result))
                self._skip_block = not expr_result
        else:
            self._php_stub = True

        if self._php_stub:
            return "<?php if ($%s) { ?>" % self._variable_str
        return ""

    @staticmethod
    def get_regex_params():
        return ["p_var_unary_cond"]

    @staticmethod
    def get_regex():
        return r"\[\% if (?P<p_var_unary_cond>(true|false|\".+\"|[0-9]+|[A-Za-z0-9_]+)) \%\]"


class BinaryConditionalWhenExpression(BaseExpression):
    def __init__(self, settings):
        super(BinaryConditionalWhenExpression, self).__init__(settings)
        self._variable_str = settings.match.group("p_var_binary_cond")

    def __call__(self, *args, **opts):
        print("BinaryCond is '%s'" % self._variable_str)
        expression = self.settings.processor._varholder.get_variable_expression(self._variable_str)
        print("Expression type is - %s" % type(expression))
        self._php_stub = False
        self._conditional = True
        expr_result = None
        if expression:
            expr_result = expression.get_result()
            if expr_result is None:
                self._php_stub = True
            else:
                print(str(expr_result))
                self._skip_block = not expr_result
        else:
            self._php_stub = True

        if self._php_stub:
            return "<?php if ($%s) { ?>" % self._variable_str
        return ""

    @staticmethod
    def get_regex_params():
        return ["p_var_binary_cond"]

    @staticmethod
    def get_regex():
        return r"\[\% if (?P<p_var_binary_cond>(true|false|\".+\"|[0-9]+|[A-Za-z0-9_]+) == (true|false|\".+\"|[0-9]+|[A-Za-z0-9_]+)) \%\]"


class ConditionalEndExpression(BaseExpression):
    def __init__(self, settings):
        super(ConditionalEndExpression, self).__init__(settings)

    def __call__(self, *args, **opts):
        self._conditional = False        
        self._skip_block = False
        if self._php_stub:
            self._php_stub = False
            return "<?php } ?>"
        return ""

    @staticmethod
    def get_regex_params():
        return ["p_end_block"]

    @staticmethod
    def get_regex():
        return r"\[\% (?P<p_end_block>end) \%\]"


class ConditionalUnlessExpression(BaseExpression):
    def __init__(self, settings):
        super(ConditionalUnlessExpression, self).__init__(settings)

    def __call__(self, *args, **opts):
        if self._php_stub:
            return "<?php } else { ?>"

        print("Skip block is %s" % self._skip_block)
        self._skip_block = not self._skip_block
        print("Skip block is %s now" % self._skip_block)
        return ""

    @staticmethod
    def get_regex_params():
        return ["p_else_block"]

    @staticmethod
    def get_regex():
        return r"\[\% (?P<p_else_block>else) \%\]"