from __future__ import absolute_import
from . import BaseIncludeExpression


class IncludeExpression(BaseIncludeExpression):
    def __init__(self, asset, match):
        super(IncludeExpression, self).__init__(asset, match, "scripts", "_%s")

    @staticmethod
    def get_regex():
        return r"\[\%= include \"(?P<p_include_path>[a-zA-Z0-9_\-]+\.(js|coffee))\" \%\]"
