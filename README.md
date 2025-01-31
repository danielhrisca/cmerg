# cmerg
Python parser for CarMaker ERG files with Pandas DataFrame export.

##

## Use and Examples

Mostly these are notes for myself but hopefully someone else finds them useful.

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

Dictionary of the signals in the file.

``` log1.signals ```

Save the vehicle speed signal to a variable.

``` speed = log1.get('Vhcl.v') ```

Plot signal.

``` speed.plot() ```

Add signal to DataFrame.

``` python

# New easy call to return a pandas DataFrame.
df = log1.to_pd()

```

``` python

# Simple example of adding ERG data to pandas.
import cmerg
import pandas as pd
import numpy as np

log1 = cmerg.ERG('data-file.erg')

speed = log1.get('Vhcl.v')

t = np.array(speed.timestamps)
spd = np.array(speed.samples)

df = pd.DataFrame({'time': t, 'speed': spd})

```

Export ERG file to CarMaker compliant csv (e.g. for import using `Import from File`)

```python
log1 = cmerg.ERG('data-file.erg')
log1.export_cm_csv("./target.csv")

# it's also possible to export only quantities that matches a namespace:
log1.export_cm_csv("./target.csv", columns_filter=["Car_"])

# CM's Import from File cannot handle many digits well, therefore the exported values are rounded. The number of digits can be sepcified:
log1.export_cm_csv("./target.csv", columns_filter=["Car_"], digits=5)
```