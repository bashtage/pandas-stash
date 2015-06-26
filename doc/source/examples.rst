Naming the HDF file
-------------------
The default output is names *workspace.h5*.  This file will be overwritten
whenever a new stash is made in the same working directory.

.. code-block:: python

    from pandas-stash import stash, unstash
    apple, banana, cherry, date, eugenia, fig  = 1, 2, 3, 4, 5, 6
    stash('keep_these_results.h5')  # Save to keep_these_results
    vault = unstash('keep_these_results.h5')


Selecting data types to store
-----------------------------
Keyword arguments can be used to select the type of objects to store -- pandas,
numpy and/or scalars.

.. code-block:: python

    import numpy as np
    from pandas-stash import stash, unstash
    apple, banana, cherry, date, eugenia, fig  = 1, 2, 3, 4, 5, 6
    a1 = np.array([1.0,2.0])
    stash(pandas=False, numpy=True, scalars=False)  # numpy only
    vault = unstash()


Wildcard Matches
----------------
Both strings and wildcard matchers can be passed as an iterable using the
keyword ``include``.  String matches must be exact, while wildcard matches can
include one ore more ``'*'`` which will match any character.

.. code-block:: python

    from pandas-stash import stash, unstash
    apple, banana, cherry, date, eugenia, fig  = 1, 2, 3, 4, 5, 6
    stash(include=['*a*','cherry'])  # Include anything with an a or cherry
    vault = unstash()
    print(vault.items)

Wildcard Exclusions
-------------------
``exclude`` can be used like the ``include`` keyword argument to exclude
variables from the stash.

.. code-block:: python

    from pandas-stash import stash, unstash
    apple, banana, cherry = 1, 2, 3
    stash(exclude['*a*'])  # Exclude apply and banana
    vault = unstash()
    print(vault.items)

**Note**: Includes are processed before excludes, so that if a variable matches
an include wildcard or string, then it will be included.  ``stash`` is
conservative in the sense that it is more likely to preserve data.


Including private variables
---------------------------
Private variables -- those starting with ``_`` -- are excluded by default. To
include private variables, use the keyword argument ``private=True``.

.. code-block:: python

    from pandas import DataFrame
    from pandas-stash import stash, unstash
    df = DataFrame(['a', 'b'])
    _df = DataFrame([1.0,2.0])
    stash(private=True)
    vault = unstash()
    print(vault.items)

Storing and loading a dictionary
--------------------------------
``stash`` will attempt to get access to ``gobals()``.  This can be overwritten
with a different frame (e.g. ``locals()``) or a dictionary-like object can be
passed containing only the variables to save. Similarly, a dictionary-like
object can be passed to ``unstash`` to place the loaded values into a
particular frame.

.. code-block:: python

    from pandas import DataFrame
    from pandas-stash import stash, unstash
    d = dict(apple=1, banana=2, cherry=3)
    stash(frame=d)  # Save from d
    new_frame = {}
    vault = unstash(frame=locals())  # Load to locals