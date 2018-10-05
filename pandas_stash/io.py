from collections import defaultdict
from inspect import currentframe
import warnings
from fnmatch import filter

import numpy as np
import pandas as pd

from tables.exceptions import NaturalNameWarning

from .compat import SCALAR_TYPES, long, u
from .vault import Vault

DEFAULT_PATH = 'workspace.h5'
PANDAS_TYPES = (pd.Series, pd.DataFrame)
PANDAS_NUMPY_MAP = dict([(i + 1, pd_type)
                         for i, pd_type in enumerate(PANDAS_TYPES)])
SCALAR_TYPES_LIST = tuple(SCALAR_TYPES)
NUMPY_DTYPES = {np.bool: 'bool',
                np.int8: 'int8',
                np.int16: 'int16',
                np.int32: 'int32',
                np.int64: 'int64',
                np.uint8: 'uint8',
                np.uint16: 'uint16',
                np.uint32: 'uint32',
                np.uint64: 'uint64',
                np.float32: 'float32',
                np.float64: 'float64',
                np.str: 'str'}
NUMPY_DTYPES_LIST = tuple(NUMPY_DTYPES)


class UnsupportedDimensionWarning(Warning):
    pass


unsupported_dimension_doc = """
Unsupported numpy array with ndim={0}. Only ndim in (1,2,3,4) supported.
"""


class UnsupportedValueWarning(Warning):
    pass


unsupported_value_doc = """
{0} is a scalar long/integer that is larger than the maximum int64 value,
and so cannot be saved.
"""


def _is_string_type(dtype):
    try:
        return dtype.type in (np.str, np.str_)
    except AttributeError:
        return False


def _print_detailed_info(header, variables):
    print(header)
    print('-' * 20)
    cts = [len(variables[key]) > 0 for key in ('pandas', 'numpy', 'builtin')]
    if not any(cts):
        print('None')
        return
    for key in ('pandas', 'numpy', 'builtin'):
        if len(variables[key]) > 0:
            print(' ' + key.capitalize())
            print(' ' + '-' * 16)
            for dtype in sorted(variables[key].keys()):
                line = ' ' + dtype + ': '
                lhs_margin = ' ' * len(line)
                subkeys = sorted(variables[key][dtype])
                for subkey in subkeys:
                    subkey_len = len(subkey) + 2
                    if len(line) + subkey_len > 80:
                        print(line)
                        line = lhs_margin
                    line += subkey + ', ' if subkey != subkeys[-1] else subkey
                print(line)
            print(' ')


class Saver(object):
    """
    Save the contents of your workspace -- pandas, numpy or scalars

    Parameters
    ----------
    path: str, optional
        Full path of file to save.  If omitted uses ./workspace.h5
    pandas: bool, optional
        Flag indicating to include pandas objects (Series, DataFrame)
    scalars: bool, optional
        Flag indicating whether to save scalars (float, int, string)
    numpy: bool, optional
        Flag indicating whether to save numpy arrays (1-4 dimension, most
        dtypes except complex)
    frame: dict-like, optional
        Dictionary-like structure that supports key-based access (e.g.
        globals()).  Uses the frame of the calling namespace if not given.
    private: bool, optional
        Flag indicating whether to include variables starting with
        underscore (``_``)
    include: iterable of str, optional
        Iterable containing variables names to store or wildcard patterns to
        match (e.g. ``ap*le`` or ``*pple``)
    exclude: iterable of str, optional
        Iterable containing variables names to exclude from the store or
        wildcard patterns to match (e.g. ``ap*le`` or ``*pple``)
    verbose: bool, optional
        Flag indicating whether to display information about variables stored.
    kwargs: optional
        optional additional arguments to pass to HDFStore when creating the
        store. Can include values such as compression variables (complib,
        complevel)

    Notes
    -----
    Does not currently support complex-valued numpy arrays.
    Includes are processed before excludes, so values that match both will be
    included.
    """

    def __init__(self, path=None, pandas=True, scalars=True, numpy=True,
                 frame=None, private=False, include=None, exclude=None,
                 verbose=True, **kwargs):
        self._path = 'workspace.h5' if path is None else path
        _globals = currentframe().f_back.f_globals
        self._frame = _globals if frame is None else frame
        if not issubclass(type(self._frame), dict):
            raise TypeError('frame must be dict-like if provided.')
        self._pandas = pandas
        self._scalars = scalars
        self._numpy = numpy
        if 'complib' not in kwargs:
            kwargs['complib'] = 'blosc'
        if 'complevel' not in kwargs:
            kwargs['complevel'] = 1
        self._kwargs = kwargs
        self._private = private
        self._pandas_vars = []
        self._numpy_vars = []
        self._scalar_vars = []
        self._store = None
        self._verbose = verbose
        self._variables = dict([(key, defaultdict(list))
                                for key in ('pandas', 'numpy', 'builtin')])
        self._include = include
        self._exclude = exclude

    def open(self):
        """
        Open the store for writing
        """
        self._store = pd.HDFStore(self._path, mode='w', **self._kwargs)

    def write(self):
        """
        Write data to an open store.
        """
        self._select_variables()
        if self._pandas:
            self._write_pandas()
        if self._scalars:
            self._write_scalars()
        if self._numpy:
            self._write_numpy()
        if self._verbose:
            _print_detailed_info('Variables Saved', self._variables)

    def _select_variables(self):
        frame = self._frame
        candidates = list(frame.keys())
        pandas = []
        numpy = []
        scalars = []
        wildcard_matches = []
        if self._include is not None:
            for incl in self._include:
                if incl.find('*') >= 0:
                    wildcard_matches.extend(filter(candidates, incl))
            candidates = [candidate for candidate in candidates
                          if candidate in self._include]
            candidates = set(candidates + wildcard_matches)
        elif self._exclude is not None:
            excluded = [candidate for candidate in candidates
                        if candidate in self._exclude]
            for excl in self._exclude:
                if excl.find('*') >= 0:
                    wildcard_matches.extend(filter(candidates, excl))
            excluded = excluded + wildcard_matches
            candidates = set(candidates).difference(excluded)

        for candidate in candidates:
            if not self._private and candidate.startswith('_'):
                continue
            obj = frame[candidate]
            if isinstance(obj, PANDAS_TYPES):
                pandas.append(candidate)
            elif isinstance(obj, SCALAR_TYPES_LIST):
                scalars.append(candidate)
            elif isinstance(obj, np.ndarray):
                dtype = getattr(obj, 'dtype', None)
                if (dtype in NUMPY_DTYPES_LIST or _is_string_type(dtype)) \
                        and obj.ndim in (1, 2, 3, 4):
                    numpy.append(candidate)
                elif (dtype in NUMPY_DTYPES_LIST and
                        obj.ndim not in (1, 2, 3, 4)):
                    warnings.warn(unsupported_dimension_doc.format(obj.ndim),
                                  UnsupportedDimensionWarning)

        self._pandas_vars = pandas
        self._numpy_vars = numpy
        self._scalar_vars = scalars

    def close(self):
        """
        Close an open store
        """

        self._store.close()

    def _write_pandas(self):
        frame = self._frame
        store = self._store
        warnings.simplefilter('ignore', NaturalNameWarning)
        for key in self._pandas_vars:
            store.append('pandas:' + key, frame[key], index=False)
            pandas_type = str(type(frame[key])).split('.')[-1].split("'")[0]
            self._variables['pandas'][pandas_type].append(key)
        warnings.simplefilter('default', NaturalNameWarning)

    def _write_scalars(self):
        frame = self._frame
        values = defaultdict(dict)
        store = self._store
        for key in self._scalar_vars:
            if (type(frame[key]) in (int, long) and
                    frame[key] > np.iinfo(np.int64).max):
                warnings.warn(unsupported_value_doc.format(key),
                              UnsupportedValueWarning)
                continue
            values[type(frame[key])][key] = frame[key]
            _type = SCALAR_TYPES[type(frame[key])]
            self._variables['builtin'][_type].append(key)

        warnings.simplefilter('ignore', NaturalNameWarning)
        for key in values:
            items = values[key]
            hdf_key = 'builtin:' + SCALAR_TYPES[key]
            store.put(hdf_key, pd.Series(items), format='fixed')
        warnings.simplefilter('default', NaturalNameWarning)

    def _write_numpy(self):
        store = self._store
        frame = self._frame
        warnings.simplefilter('ignore', NaturalNameWarning)
        for key in self._numpy_vars:
            obj = frame[key]
            dtype = obj.dtype
            pd_obj = PANDAS_NUMPY_MAP[obj.ndim](obj, dtype=dtype)
            hdf_key = 'numpy:' + str(dtype) + ':' + key
            store.append(hdf_key, pd_obj, index=False)
            self._variables['numpy'][str(dtype)].append(key)
        warnings.simplefilter('default', NaturalNameWarning)


class Loader(object):
    """
    Loads the contents of a file created by stash

    Parameters
    ----------
    path: str, optional
        Full path of file to save.  If omitted uses ./workspace.h5
    insert: bool, optional
        Flag indicating whether to insert into frame
    frame: dict-like, optional
        Dictionary-like structure that supports key-based access (e.g.
        globals()).  Uses the frame of the calling namespace if not given
    overwrite: bool, optional
        Flag indicating whether to overwrite existing values in the frame
    verbose: bool, optional
        Flag indicating whether to display information about variables loaded

    """

    def __init__(self, path=None, insert=True, frame=None, overwrite=False,
                 verbose=True):
        self._path = DEFAULT_PATH if path is None else path
        _globals = currentframe().f_back.f_globals
        self._frame = _globals if frame is None else frame
        self._insert = insert
        self._overwrite = overwrite
        self._vault = Vault()
        self._verbose = verbose
        self._variables = dict([(key, defaultdict(list))
                                for key in ('pandas', 'numpy', 'builtin')])

    def _load_pandas(self, key, item):
        variable_name = key.split(':')[-1]
        self._vault[variable_name] = item
        klass = item.__class__.__name__
        self._variables['pandas'][klass].append(variable_name)

    def _load_numpy(self, key, item):
        variable_name = key.split(':')[-1]
        dtype = key.split(':')[-2]
        self._vault[variable_name] = np.array(item, dtype=dtype)
        self._variables['numpy'][dtype].append(variable_name)

    def _load_scalars(self, key, items):
        builtin_type = key.split(':')[-1]
        converters = {'str': str, 'float': float, 'int': int, 'unicode': u}
        for index, val in items.iteritems():
            self._vault[index] = converters[builtin_type](val)
            self._variables['builtin'][builtin_type].append(index)

    def load(self):
        """
        Load a stash

        Returns
        -------
        vault : Vault
        dict-like object that supports tab completion for keys in IPython
        """
        store = pd.HDFStore(self._path, mode='r')
        keys = store.keys()
        for key in keys:
            item = store.get(key)
            key = key.replace('/', '')
            if key.startswith('pandas'):
                self._load_pandas(key, item)
            elif key.startswith('numpy'):
                self._load_numpy(key, item)
            elif key.startswith('builtin'):
                self._load_scalars(key, item)
        if self._insert:
            for key in self._vault:
                if self._overwrite or key not in self._frame:
                    self._frame[key] = self._vault[key]
        if self._verbose:
            _print_detailed_info('Variables Loaded', self._variables)
        store.close()
        return self._vault
