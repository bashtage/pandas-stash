"""
Inspired by Bunch, only simpler.
"""
from .compat import iterkeys, string_types

RESERVED = dir({}) + ['items']


class ReservedWordWarning(Warning):
    pass


class Vault(dict):
    """
    A dictionary that also supports assignment or access using attributes.

    >>> v = Vault()
    >>> v.a = 'apple'
    >>> v['b'] = 'apple'
    >>> v.a == v['b']

    Notes
    -----
    Use items to access the list of objects stored in the vault
    """

    def __contains__(self, k):
        """
        Allows use as in x in vault
        """
        return dict.__contains__(self, k)

    def __setattr__(self, key, value):
        if key in RESERVED:
            raise AttributeError('{0} is a reserved attribute.  This key can '
                                 'only be set using dictionary syntax.')
        self[key] = value

    @property
    def items(self):
        """
        Return list of items in the vault
        """
        return sorted(self.keys())

    def __getattribute__(self, item):
        if item in RESERVED and item in self:
            from warnings import warn
            warn('{0} is a reserved attribute but is also in this vault. '
                 'Reserved attributed can only be accessed using dictionary '
                 'syntax.'.format(item), ReservedWordWarning)

        return object.__getattribute__(self, item)

    def __getattr__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            raise AttributeError(item)

    def __dir__(self):
        keys = [key for key in iterkeys(self) if isinstance(key, string_types)]
        return sorted(['items'] + keys)
