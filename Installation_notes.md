# Installation notes

Here we record in a loose fashion some observations, issues and possible fixes for PYME installation with `PYME-test-env` as we observe it. Entries should be dated and newest should be at the top.

## 4.6.25

We keep pinning `setuptools<=73` and this will likely remain until the build
system of `PYME` (and by extension, `PYME-extra`) has been overhauled to drop `numpy.distutils` dependencies. This is a major job and limits installation
to `Python<3.12` for now.

Builds with 3.10 and 3.11 should now work out of the box. Consult the file [current-commands.md](current-commands.md) for suggested command sequences.

It is also possibly to build with numpy>=2 with a patch/PR for PYME. Further details are in [current-commands.md](current-commands.md).



## 21.9.24

### python 3.X/numpy issues

The latest issues with installing PYME with python 3.x have been traced to a change in `setuptools`. `setuptools>73` on mac (and possibly linux) appear to have stopped packaging a distutils file relating to some of the windows compilers. This exposed an unconditional import from `numpy.distutils` in some of the cython build logic, i.e. the issue described in [this numpy bug report](https://github.com/numpy/numpy/issues/27405).

For now appears to be solvable by pinning `setuptools<=73`.

#### UPDATE 24.9.24: this is also an issue on windows

We have therefore also pinned `setuptools<=73` on windows for now. Possibly once numpy 1.x with [this fix](https://github.com/numpy/numpy/pull/27406) become available this could be relaxed - but not sure if/when this will happen.

## 20.9.24

### python 3.X/numpy issues

When installing with python 3.11 current `numpy.distutils` appears to have a regression that hickups running `setup.py` for PYME on mac. The issue is the one referenced in [this numpy bug report](https://github.com/numpy/numpy/issues/27405). It also proposes [a fix](https://github.com/numpy/numpy/pull/27406) that has been merged but not sure in which numpy 1.X version this will still be considered.

General observation is that `numpy.distutils` is on the way out (see below) and may become increasingly flaky.

Not sure how the issue is triggered, i.e. is it a consequence of python 3.11? At least until yesterday 3.10 builds did not show this error. Comparison shows numpy version is the same between the 3.10 and 3.11 installs.

python 3.11 builds can currently be fixed by manually applying the patch in [the merged fix](https://github.com/numpy/numpy/pull/27406).

**Additional note**: now python 3.10 builds also fail in this way. Not sure what changed since seemingly numpy versions etc are the same across a couple of 3.10 envs I have. One from a few days agao where everything was fine, today with otherwise apparently identical settings it bombs.

**Update**: see entry from 21.9.24 for proper fix

### numpy 2.x

Numpy 2.X has changed the cython interface for C code. From a quick inspection this needs fixes in a number of PYME type cython files. Not sure how to achieve the fixes yet, when skimming the docs no obvious migration path/example seemed to be discussed. Probably requires more digging.

#### Implicit pinning of numpy 1.X

Currently we are pinning `matplotlib<=3.8` which appears to result in a `numpy 1.X `downgrade. If we are unpinning matplotlib then we may need to pin numpy at 1.X or fix the issue for good with numpy 2.X. At this stage no idea if numpy 2.X has other implications for PYME.

### python 3.12 and numpy.distutils

`numpy.distutils` has been deprecated for a while and disappears with python 3.12, see also [here](https://numpy.org/doc/stable/reference/distutils_status_migration.html). Sooner or later we will need a replacement, the migration document mentions a few possibilities...

Sounds like a reasonably big job.
