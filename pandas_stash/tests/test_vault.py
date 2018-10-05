import warnings

from pandas_stash.vault import Vault, ReservedWordWarning
import pytest


class TestVault(object):
    def test_smoke(self):
        vault = Vault()
        vault.a = 'a'
        vault['b'] = 'b'
        assert vault.b == 'b'
        assert vault.a == 'a'
        assert vault['a'] == 'a'
        assert vault['b'] == 'b'

    def test_construction(self):
        vault = Vault()
        items = [1, 2.0, 'a', 'cat']
        for item in items:
            vault[item] = item

        for key in vault:
            assert vault[key] in items

        for item in items:
            assert item in vault

        assert 'b' not in vault

    def test_set_attribute(self):
        vault = Vault()
        vault.a = 'a'
        vault.cat = 'cat'
        items = ['a', 'cat']
        for item in items:
            assert item in vault
            assert vault[item] == item
            assert vault[item] == getattr(vault, item)

    def test_del_attribute(self):
        vault = Vault()
        vault.a = 'a'
        vault.cat = 'cat'
        del vault['a']
        assert 'a' not in vault
        assert 'cat' in vault

    def test_reserved(self):
        vault = Vault()
        vault['keys'] = 'keys'
        with pytest.raises(AttributeError):
            vault.keys = 'keys'

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            var = vault.keys
            assert callable(var)
            assert len(w) == 1
            assert issubclass(w[-1].category, ReservedWordWarning)

    def test_items(self):
        vault = Vault()
        vault['a'] = 1
        vault['b'] = 'b'
        assert sorted(vault.items) == sorted(vault.keys())
        assert sorted(['items'] + vault.items) == sorted(dir(vault))
