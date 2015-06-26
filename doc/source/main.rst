Main functions
==============

.. py:module:: pandas_stash

.. py:currentmodule:: pandas_stash

.. autofunction:: stash

.. autofunction:: unstash

.. py:currentmodule:: pandas_stash.io

Low-level Access
================
These two classes lie under ``stash`` and ``unstash`` and are used to structure
the saving and restoring of data.  Their external API should not be considered
stable.

.. autoclass:: Saver
    :members: open, write, close

.. autoclass:: Loader
    :members: load

Vault
=====
A ``Vault`` is the dictionary-like class used to load results.  It supposed
 access by attributes to make it friendly in an IPython terminal.

.. py:currentmodule:: pandas_stash.vault

.. autoclass:: Vault



