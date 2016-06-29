# flake8: noqa
import sys

PY3 = sys.version_info[0] >= 3
PY2 = sys.version_info[0] == 2

SCALAR_TYPES = {int: 'int', str: 'str', float: 'float'}
if PY2:
    SCALAR_TYPES[unicode] = 'unicode'


    def u(s):
        if isinstance(s, unicode):
            return s
        else:
            return unicode(s, "unicode_escape")


    string_types = basestring
    long = long
else:
    long = int
    u = lambda s: s
    string_types = str


def iteritems(obj, **kwargs):
    """replacement for six's iteritems for Python2/3 compat
       uses 'iteritems' if available and otherwise uses 'items'.

       Passes kwargs to method.
    """
    func = getattr(obj, "iteritems", None)
    if not func:
        func = obj.items
    return func(**kwargs)


def iterkeys(obj, **kwargs):
    """replacement for six's iteritems for Python2/3 compat
       uses 'iteritems' if available and otherwise uses 'items'.

       Passes kwargs to method.
    """
    func = getattr(obj, "iterkeys", None)
    if not func:
        func = obj.keys
    return func(**kwargs)


try:
    from unittest import skipIf
except ImportError:
    from unittest2 import skipIf


def skip_if(cond, msg=''):
    return skipIf(cond, msg)
