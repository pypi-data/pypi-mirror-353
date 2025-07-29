# PlasmaCalcs

PlasmaCalcs provides a consistent interface (in Python) for plasma calculations from any inputs.

Online docs available at https://plasmacalcs.readthedocs.io


# Examples and Guides

- [getting-started\_eppic.ipynb](https://gitlab.com/Sevans7/plasmacalcs/-/blob/main/examples/getting-started_eppic.ipynb) is a good place for anyone to get started. Even though some details are specific to eppic, most of it is generic enough to be useful to everyone. Estimated time: 5 mins.

- [tfbi\_theory\_example.ipynb](https://gitlab.com/Sevans7/plasmacalcs/-/blob/main/examples/tfbi_theory_example.ipynb) shows some examples of solving the Thermal Farley-Buneman Instability theory, via the [tfbi\_theory](https://pypi.org/project/tfbi_theory) package. That package solves the theory itself, but `PlasmaCalcs` loads all the relevant inputs and helps with analyzing the results. Estimated time: 2-3 mins.

[TODO] add more examples!


# Installation

You can install the [latest release](https://pypi.org/project/PlasmaCalcs/) via:
```bash
pip install plasmacalcs
```

Or, you can install directly from git:
```bash
cd directory_where_you_want_this_code_to_be_installed
git clone https://gitlab.com/Sevans7/plasmacalcs
cd PlasmaCalcs  # into the directory where the pyproject.toml can be found.
pip install -e .   # you can drop the "-e" if you will never edit PlasmaCalcs.
```

You also might want to install with most optional dependencies:
```bash
# if installing the latest release:
pip install "plasmacalcs[most]"
# OR, if installing directly from git (replace "pip install -e ." above):
pip install -e ".[most]"
```
Using `[most]` includes most optional dependencies. Also consider `[all_fast]` which additionally includes packages with a small userbase (e.g. less than 100 users), and `[all]` which additionally includes packages with a long installation time (e.g. more than a few seconds).


# Misc. Additional Examples

[TODO] move these examples to a different document (remove from README). Also, double-check that these examples actually still work...

## Generic PlasmaCalculator
In practice you will probably use a specific PlasmaCalculator subclass connected to your type of input (e.g., EppicCalculator or EbysusCalculator). But, all PlasmaCalculators have many things in common, so this example is a good place to start.
```python
import PlasmaCalcs as pc
p = pc.PlasmaCalculator()
p('xhat')  # xarray.DataArray with values [1,0,0] along 'component' dimension with coordinates x, y, z components.
p('100-7*8/(5+2)')  # PlasmaCalculator objects recognize integers and any simple arithmetic (+,-,/,*,**)

# some helpful things know about while you're getting started, include:
p.help()  # helps you learn which variables & patterns are recognized by this PlasmaCalculator object.
p.match_var_tree('xhat_cross_yhat')  # display tree of quantities p will load to get 'xhat_cross_yhat'. Best viewed in Jupyter.
p.behavior  # dict of all attributes of p that might affect its outputs. e.g. includes 'units'.

# -- important concept --
# when getting values, PlasmaCalcs will include the result at all "current value(s)" of each relevant Dimension.
# E.g., you can set the component to 0, then the result will only include the x component
#   (or still include no components if the result is not associated with any component in particular.)
p.component = 0
p('xhat')   # xarray.DataArray with value 1, including 'component' coordinate showing x component only.
p('100+7')  # xarray.DataArray with value 107. No 'component' coordinate because it doesn't depend on component.
# you can also set any Dimension's current value using a list, slice, or range:
p.component = [0,1]
p.component = slice(0, 2)  # equivalent to previous line
p.component = range(2)     # equivalent to previous line
p('xhat')   # xarray.DataArray with values [1,0] along 'component' dimension with coordinates x, y components.
# you can use None to say "use all possible values"
p.component = None   # equivalent to p.component = p.components
# finally, you may want to compare DimensionValue objects to strings or ints; you can do that!
# e.g.:
p.component = 'x'  # equivalent to p.component = 0
p.component == 'x'  # True
p.component == 0   # True
p.component is x   # False! p.component is a DimensionValue object. It can be converted & compared to int or str, though.
p.component is p.components[0]  # True
p.component = [0,'z']   # equivalent to p.component = [0, 2]   # equivalent to p.component = ['x', 'z']

# note - "main dimensions" (e.g. x,y dimensions of a simulation with 512x512 grid in x,y) are handled differently;
# see MainDimensionsHaver in the code, for more details.
```

## EbysusCalculator
EbysusCalculator is initialized by providing an EbysusData object from helita. The idea is that it will use EbysusData as an interface for getting values from files, but use PlasmaCalcs for doing any of the heavy lifting. It will also center all variables on the stagger grid so that other calculations do not need to worry about stagger mesh calculations.
```python
import PlasmaCalcs as pc
from helita.sim import eb
dd = eb.EbysusData(...)  # you need to fill in the info here.
ec = pc.EbysusCalculator(dd)
ec('gyrof')  # gyrofrequency. (will have snap & fluid matching dd.snap & dd.fluid)
ec.snap = None  # load across all snaps. Like dd.get_varTime.
ec('gyrof')
ec.snap = slice(0, None, 10)  # load from every 10th snapshot.
ec.fluid = None   # load across all fluids.
ec('gryof')

ec.dimensions   # view all dimensions associated with this EppicCalculator (probably will be 'snap', 'component', 'fluid', and 'jfluid')

# for more examples see example above, in the "Generic PlasmaCalculator" section.
# also try help(ec)
# also try ec.help()
```

## EppicCalculator
You will probably create it using `EppicCalculator.from_here()`, after changing to a directory containing an "eppic.i" file.


## Plotting
xarray has some pretty good plotting routines available, attached to the arrays as methods. See `xarray.DataArray.plot` for details.  
Additionally, PlasmaCalcs provides some custom plotting routines attached to xarray objects; these are quite useful for making movies or making line plots of many values vs time on the same axes. See:
```python
arr = ...  # any xarray.DataArray. Possibly the output of a PlasmaCalculator object.
arr.pc    # The object which stores methods related to xarrays which are defined in PlasmaCalcs.
arr = ...  # provide an xarray.DataArray with 'fluid' dimension. Maybe also 't' or 'snap' dimension. Definitely 2 other dimensions e.g. 'x', 'y'.
xsubs = arr.pc.subplots(row='fluid')  # make a row of 2d plots with a different fluid in each.
arr = ...  # provide an xarray.DataArray with 'fluid', 'component', and 'snap' or 't' dimensions. Also 2 other dimensions e.g. 'x', 'y'.
xsubs = arr.pc.subplots(row='fluid', col='components')  # grid of 2d plots with a different fluid & component in each.
xsubs(17).fig   # figure at 17th frame. If this line appears at end of a Jupyter cell, display that figure.
xsubs.get_animator()   # get FuncAnimation object which will plot the movie. Optional. If at end of a Jupyter cell, may render the movie in-line.
xsubs.save('mymovie.mp4', frames=slice(0, None, 10))  # save movie to a file. here, frames indicates to only save every 10th frame.

arr = ...  # provide an xarray.DataArray with 't' or 'snap' dimension, as well as any other dimensions. Probably no very long dimensions.
tls = arr.pc.timelines()  # plot lines vs 't', e.g. fluid, component = (0,0), (0,1), (0,2), (1,0), ..., (4,2) if arr has fluids 0-4 and components 0-2.
```

[TODO] show off a few plots directly in the README!


# Contributing
Happy to accept contributions.
At this stage in development, the easiest way to contribute is to ask for permission to push commits directly to this repo.
Currently allowing people to push directly to `main` (merge requests not required).
Though, if you're working on any big features, it's better practice to make a new branch, then submit a merge request to merge into main when you're done.

If making a new branch sounds scary, or if you're not super familiar with git, consider [GitHub Desktop](https://github.com/apps/desktop); it helps make git way more intuitive and less painful to use.

Note there are tests in the tests folder; if you are able to add any tests which test new or existing PlasmaCalcs code, please do! They are run automatically whenever someone commits to this repo.

# License
Licensed under the MIT License; see also: LICENSE

# Project status
Actively developing & using this project.
