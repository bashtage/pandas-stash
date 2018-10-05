import warnings

import numpy as np
import pandas as pd
import pytest
from pandas.util.testing import ensure_clean

from pandas_stash import stash, unstash
from pandas_stash.compat import PY2 as _PY2
from pandas_stash.io import UnsupportedDimensionWarning, UnsupportedValueWarning


class TestVault(object):
    def test_smoke(self):
        global a
        a = 'a'
        with ensure_clean() as path:
            stash(path, verbose=False)
            del a
            vault = unstash(path, verbose=False)
            assert 'a' in vault
            assert 'a' in globals()
            assert a == 'a'
            del a

    def test_pandas(self):
        global df, s_int32, s_int64, s_int16, s_int8
        s_int8 = pd.Series([1, 2, 3], dtype=np.int8)
        s_int16 = pd.Series([1, 2, 3], dtype=np.int16)
        s_int32 = pd.Series([1, 2, 3], dtype=np.int32)
        s_int64 = pd.Series([1, 2, 3], dtype=np.int64)
        df = dict(('s' + str(i), s) for i, s in enumerate([s_int8, s_int16, s_int32, s_int64]))
        df = pd.DataFrame(df)
        df['float32'] = np.array([1.0, 2.0, 3.0], dtype=np.float32)
        df['float64'] = np.array([1.0, 2.0, 3.0], dtype=np.float64)
        variables = ['s_int8', 's_int16', 's_int32', 's_int64', 'df']
        with ensure_clean() as path:
            stash(path, verbose=False)
            _g = globals()
            for v in variables:
                del _g[v]
            vault = unstash(path, verbose=False)
            assert 's_int8' in vault
            assert 's_int16' in vault
            assert 's_int32' in vault
            assert 's_int64' in vault
            assert 'df' in vault
            for v in variables:
                del _g[v]

    def test_numpy(self):
        global complex128
        dtypes = [np.uint8, np.uint16, np.uint32, np.float32, np.float64,
                  np.int8, np.int16, np.int32, np.int64, np.bool]
        _g = globals()
        for i, dtype in enumerate(dtypes):
            _g['np_' + str(i)] = np.array([0, 1, 2, 3], dtype=dtype)
            complex128 = np.array([0, 1, 2, 3], dtype=np.complex128)
        with ensure_clean() as path:
            stash(path, verbose=False)
            vault = unstash(path, verbose=False)
        dicts = [globals(), vault]
        names = ['np_' + str(i) for i in range(len(dtypes))]
        for dic in dicts:
            for n in names:
                assert n in dic
        for n in names:
            del globals()[n]
        del complex128

    def test_scalars(self):
        global a, b, c, d, e, f
        a, b, c, d, e, f = 1.0, -1.0, 1, -1, 'str', u'unicode'
        with ensure_clean() as path:
            stash(path, verbose=False)
            del a, b, c, d, e, f
            vault = unstash(path, verbose=False)
            for key in ('a', 'b', 'c', 'd', 'e', 'f'):
                assert key in globals()
                assert key in vault
        del a, b, c, d, e, f

    def test_verbose(self):
        global a, b, c, d
        a = 'a'
        b = 1
        c = pd.DataFrame([1.0, 2.0, 3.0], columns=['A'])
        d = np.array(c)
        with ensure_clean() as path:
            stash(path, verbose=True)
            unstash(path, verbose=True)
        del a, b, c, d

    def test_include(self):
        global a, apple, anagram, banana
        a = 'a'
        apple = 'apple'
        anagram = 121
        banana = 'minion'
        with ensure_clean() as path:
            stash(path, include=['a', 'a*'], verbose=False)
            del a, apple, anagram, banana
            vault = unstash(path, verbose=False)
            assert 'a' in vault
            assert 'apple' in vault
            assert 'anagram' in vault
            assert 'banana' not in vault
        del a, apple, anagram

    def test_exclude(self):
        global apple, banana, cherry, date
        apple, banana, cherry, date = 1, 2, 3, 4
        with ensure_clean() as path:
            stash(path, exclude=['*a*'])
            del apple, banana, cherry, date
            vault = unstash(path, verbose=True)
            assert 'cherry' in globals()
            assert 'cherry' in vault
            for key in ('apple', 'banana', 'date'):
                assert key not in globals()
                assert key not in vault
        del cherry

    def test_long_variable_names(self):
        global this_is_a_long_name, this_is_another_long_name
        global this_is_a_third_long_name
        this_is_a_long_name = pd.DataFrame([1, 2, 3])
        this_is_another_long_name = pd.DataFrame([1, 2, 3])
        this_is_a_third_long_name = pd.DataFrame([1, 2, 3])
        with ensure_clean() as path:
            stash(path, verbose=True)
            del this_is_a_long_name, this_is_another_long_name, \
                this_is_a_third_long_name
            unstash(path, verbose=True)
        del this_is_a_long_name, this_is_another_long_name, \
            this_is_a_third_long_name

    def test_empty(self):
        with ensure_clean() as path:
            stash(path, exclude=['*'])
            vault = unstash(path)
            assert len(vault.items) == 0

    @pytest.mark.skipif(_PY2, reason='Buggy warnings on Python 2.x')
    def test_warnings_large_int(self):
        global e
        e = 2 ** 65
        with ensure_clean() as path:
            with pytest.warns(UnsupportedValueWarning):
                stash(path, verbose=False)
                unstash(path, verbose=False)
        del e

    def test_warnings_errors(self):
        global e
        e = np.zeros((2, 2, 2, 2, 2))
        with ensure_clean() as path:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter('always')
                stash(path, verbose=False)
                unstash(path, verbose=False)
                assert len(w) == 1
                assert issubclass(w[-1].category, UnsupportedDimensionWarning)

        e = np.zeros((2,))
        with ensure_clean() as path:
            with pytest.raises(TypeError):
                stash(path, frame=[e], verbose=False)
        del e

    def test_overwrite(self):
        global a, b, c, d
        a, b, c, d = 1, 'a', 'one', 'aye'
        with ensure_clean() as path:
            stash(path, verbose=False)
            del a, b, c
            d = 'something else'
            vault = unstash(path, verbose=False, overwrite=False)
        assert d == 'something else'
        assert 'd' in vault
        assert vault.d == 'aye'
        del d

    def test_insert(self):
        global a, b, c, d
        a, b, c, d = 1, 'a', 'one', 'aye'
        with ensure_clean() as path:
            stash(path, verbose=False)
            del a, b, c, d
            vault = unstash(path, verbose=False, insert=False)
        for key in ('a', 'b', 'c', 'd'):
            assert key in vault
            assert key not in globals()

    def test_alternative_frame(self):
        global a, b, c, d
        a, b, c, d = 1, 'a', 'one', 'aye'
        frame = {'a1': a, 'b1': b, 'c1': c, 'd1': d}
        with ensure_clean() as path:
            stash(path, verbose=False, frame=frame)
            del a, b, c, d
            new_frame = {}
            vault = unstash(path, verbose=False, frame=new_frame)
        for key in ('a1', 'b1', 'c1', 'd1'):
            assert key in vault
            assert key in new_frame
            assert key not in globals()

    def test_kwargs(self):
        global df
        df = pd.DataFrame(np.random.randn(1000000, 5))
        with ensure_clean() as path:
            stash(path, verbose=False, complib='blosc', complevel=9)
            del df
            import tables
            h5f = tables.open_file(path)
            table = h5f.root._f_get_child('pandas:df')._f_get_child('table')
            assert table.filters.complib == 'blosc'
            assert table.filters.complevel == 9
            h5f.close()

    def test_numpy_str(self):
        global a
        a = np.array(['apple', 'banana', 'cherry'])
        with ensure_clean() as path:
            stash(path, verbose=False)
            del a
            vault = unstash(path, verbose=False)
            assert 'a' in globals()
            np.testing.assert_array_equal(vault.a, np.array(['apple', 'banana', 'cherry']))
        del a

    def test_numpy_bool(self):
        global a
        a = np.array([1, 0, 1, 0, 1, 0], dtype=np.bool)
        with ensure_clean() as path:
            stash(path, verbose=False)
            del a
            vault = unstash(path, verbose=False)
            assert 'a' in globals()
            np.testing.assert_array_equal(vault.a, np.array([1, 0, 1, 0, 1, 0], dtype=np.bool))
        del a
