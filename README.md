# cmerg
Python parser for CarMaker ERG files with Pandas dataframe export.

##

## Use and Examples

Moslty these are notes for myself but hopefully someone else finds them useful.

### Installation

This package [is published on PyPI](https://pypi.org/project/cmerg/) under the name _cmerg_.

### Windows
``` shell

> python -m pip install -U pip
> python -m pip install cmerg

```
### Linux
``` shell

$ python3 -m pip install -U pip
$ python3 -m pip install cmerg

```

### Examples

Import the package folder.

``` import cmerg ```

Create ERG file object. (Using example file from repo)

``` log1 = cmerg.ERG('test-data/Test-Dataset-1_175937.erg') ```

List of the signals in the file.

``` log1.signals ```

Save the vehicle speed signal to a variable.

``` speed = log1.get('Vhcl.v') ```

Plot signal.

``` speed.plot() ```

Add signal to dataframe.

``` python

# New easy call to return a pandas dataframe.
df = log1.to_pd()

```

``` python

# Simple example of adding ERG data to pandas.
# TODO: Make 'toPd()' call
import cmerg
import pandas as pd
import numpy as np

log1 = cmerg.ERG('data-file.erg')

speed = log1.get('Vhcl.v')

t = np.array(speed.timestamps)
spd = np.array(speed.samples)

df = pd.DataFrame({'time':t, 'speed':spd})

```
