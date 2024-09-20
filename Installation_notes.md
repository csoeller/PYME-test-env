# Installation notes

Here we record in a loose fashion some observations, issues and possible fixes for PYME installation with `PYME-test-env` as we observe it. Entries should be dated and newest should be at the top.

## 20.9.24

### python 3.11/numpy issues

When installing with python 3.11 current `numpy.distutils` appears to have a regression that hickups running `setup.py` for PYME on mac. The issue is the one referenced in [this numpy bug report](https://github.com/numpy/numpy/issues/27405). It also proposes [a fix](https://github.com/numpy/numpy/pull/27406) that has been merged but not sure in which numpy 1.X version this will still be considered.

General observation is that `numpy.distutils` is on the way out (see below) and may become increasingly flaky.

Not sure how the issue is triggered, i.e. is it a consequence of python 3.11? At least until yesterday 3.10 builds did not show this error. Comparison shows numpy version is the same between the 3.10 and 3.11 installs.

python 3.11 builds can currently be fixed by manually applying the patch in [the merged fix](https://github.com/numpy/numpy/pull/27406).

**Additional note**: now python 3.10 builds also fail in this way. Not sure what changed since seemingly numpy versions etc are the same across a couple of 3.10 envs I have. One from a few days agao where everything was fine, today with otherwise apparently identical settings it bombs.

### numpy 2.x

Numpy 2.X has changed the cython interface for C code. From a quick inspection this needs fixes in a number of PYME type cython files. Not sure how to achieve the fixes yet, when skimming the docs no obvious migration path/example seemed to be discussed. Probably requires more digging.

#### Implicit pinning of numpy 1.X

Currently we are pinning `matplotlib<=3.8` which appears to result in a `numpy 1.X `downgrade. If we are unpinning matplotlib then we may need to pin numpy at 1.X or fix the issue for good with numpy 2.X. At this stage no idea if numpy 2.X has other implications for PYME.

### python 3.12 and numpy.distutils

`numpy.distutils` has been deprecated for a while and disappears with python 3.12, see also [here](https://numpy.org/doc/stable/reference/distutils_status_migration.html). Sooner or later we will need a replacement, the migration document mentions a few possibilities...

Sounds like a reasonably big job.
