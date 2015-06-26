.. pandas-stash documentation master file, created by
   sphinx-quickstart on Mon Jul  6 13:57:38 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

pandas-stash
------------
pandas-stash provide a simple method to save complete workspaces including:

    * pandas objects: Series, DataFrame, Panel and Panel4D
    * numpy arrays: dimensions 1 to 4
    * built-in scalar types (int, str, float)

Basic Usage
===========

.. code-block:: python

    from pandas import Series, DataFrame
    from pandas_stash import stash, unstash
    a = Series([1.0, 2.0])
    b = DataFrame('a':a, 'c':['a','c'])
    stash()  # Saves to ./workspace.h5
    del a, b
    unstash()  # Restores to memory from ./workspace.h5
    print(a)
    print(b)

Contents:

Further Examples
================
.. toctree::
   :maxdepth: 2

    Further Examples <examples>

Module Reference
================

.. toctree::
   :maxdepth: 2

    Module Reference <main>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

