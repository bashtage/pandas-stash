[![CI Status](https://travis-ci.org/bashtage/pandas-stash.svg?branch=master)](https://travis-ci.org/bashtage/pandas-stash)
[![Coverage Status](https://coveralls.io/repos/bashtage/pandas-stash/badge.svg?branch=master)](https://coveralls.io/r/bashtage/pandas-stash?branch=master)

# pandas-stash
A utility to save and load entire workspaces containing pandas objects, numpy 
arrays and scalars. Inspired by `git stash` and other programming languages 
that have simple methods to save and restore the workspace.

```python
import pandas as pd
from pandas_stash import stash, unstash()
df = pd.DataFrame([[1,2],[3,4]])
stash()
del df
unstash()
print(df)
```

By default the stash will attempt to get variables from the **global** frame. 
The keyword argument `frame` can be used to explicitly pass a particular frame.

See [advanced examples](https://github.com/bashtage/pandas-stash/blob/master/doc/source/examples.rst) for more options.

```python
stash(frame=globals())
```

## Limitations
Currently will store pandas objects:

* Series
* DataFrame
* Panel
* Panel4D

Numpy arrays with dimensions 1, 2, 3 and 4 with dtypes:

* uint8, uint16, uint32, uint64
* int8, int16, int32, int64
* float32, float64
* bool
* str

Scalar values of the type:

* int
* str
* float
* unicode

**Complex (scalar or numpy) values are *NOT* supported due to limitations 
in pandas and pytables. This should be fixed after pandas 0.17 is released**

## Requirements
* pandas>=0.15
* numpy>=1.7
* pytables>=3.0


