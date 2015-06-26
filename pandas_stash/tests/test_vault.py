from unittest import TestCase
import warnings

from pandas_stash.vault import Vault, ReservedWordWarning


class TestVault(TestCase):
    def test_smoke(self):
        vault = Vault()
        vault.a = 'a'
        vault['b'] = 'b'
        self.assertTrue(vault.b == 'b')
        self.assertTrue(vault.a == 'a')
        self.assertTrue(vault['a'] == 'a')
        self.assertTrue(vault['b'] == 'b')

    def test_construction(self):
        vault = Vault()
        items = [1, 2.0, 'a', 'cat']
        for item in items:
            vault[item] = item

        for key in vault:
            self.assertTrue(vault[key] in items)

        for item in items:
            self.assertTrue(item in vault)

        self.assertFalse('b' in vault)

    def test_set_attribute(self):
        vault = Vault()
        vault.a = 'a'
        vault.cat = 'cat'
        items = ['a', 'cat']
        for item in items:
            self.assertTrue(item in vault)
            self.assertTrue(vault[item] == item)
            self.assertTrue(vault[item] == getattr(vault, item))

    def test_del_attribute(self):
        vault = Vault()
        vault.a = 'a'
        vault.cat = 'cat'
        del vault['a']
        self.assertFalse('a' in vault)
        self.assertTrue('cat' in vault)

    def test_reserved(self):
        vault = Vault()
        vault['keys'] = 'keys'
        self.assertRaises(AttributeError, setattr, vault, 'keys', 'keys')

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            var = vault.keys
            self.assertTrue(callable(var))
            self.assertTrue(len(w) == 1)
            self.assertTrue(issubclass(w[-1].category, ReservedWordWarning))

    def test_items(self):
        vault = Vault()
        vault['a'] = 1
        vault['b'] = 'b'
        self.assertTrue(sorted(vault.items) == sorted(vault.keys()))
        self.assertTrue(sorted(['items'] + vault.items) == sorted(dir(vault)))
