import inspect

from .io import Saver, Loader


def stash(path=None, pandas=True, scalars=True, numpy=True, frame=None,
          private=False, include=None, exclude=None, verbose=True, **kwargs):
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
    if frame is None:
        _globals = inspect.currentframe().f_back.f_globals
        frame = _globals if frame is None else frame
    saver = Saver(path, pandas, scalars, numpy, frame, private, include,
                  exclude, verbose, **kwargs)
    saver.open()
    saver.write()
    saver.close()


def unstash(path=None, insert=True, frame=None, overwrite=False, verbose=True):
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

    Returns
    -------
    vault : Vault
        dict-like object that supports tab completion for keys in IPython

    """
    if frame is None:
        _globals = inspect.currentframe().f_back.f_globals
        frame = _globals if frame is None else frame
    loader = Loader(path, insert, frame, overwrite, verbose)
    return loader.load()
