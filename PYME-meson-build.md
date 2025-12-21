# Preliminary notes for meson based PYME build

## Current list of commands

The following works now on windows:

    python mk_pyme_env.py --python=3.11 --suffix=_ms2 --pyme-build-meson --matplotlib-numpy-latest --setuptools-latest --use-git -c mamba --pyme-repo csoeller/python-microscopy --pyme-branch meson-fixes --pymex-branch paraflux

and also on mac (using conda instead of mamba):

    python mk_pyme_env.py --python=3.11 --suffix=_ms1 --pyme-build-meson --matplotlib-numpy-latest --setuptools-latest --use-git --pyme-repo csoeller/python-microscopy --pyme-branch meson-fixes --pymex-branch paraflux
	
### Two step process on mac (superseded)

The following works on mac but is superseded by the command above which has the advantage of being able to set the paraflux branch on build of PYME-extra.

    python mk_pyme_env.py --python=3.11 --suffix=_meson --no-pymex --pyme-build-meson --matplotlib-numpy-latest --setuptools-latest --use-git

This uses the `--pyme-build-meson` flag and works so far although some code will need further fixes to use the importlib interface rather than package variables.

If this succeeds PYME-extra can be built with an extra command:

    python mk_extra_stuff.py --python=3.11 --suffix=_meson --use-git --xtra-sets PYME-extra

## Previous more manual approach

Currently, the process is a little bit manual until sussed out more fully. We are working from David's short [build instructions](https://github.com/python-microscopy/python-microscopy/blob/master/BUILD.md).

Eventually, this will be folded into the main build command (`mk_pyme_env.py`).

	python mk_pyme_env.py --python=3.11 --suffix=_meson --no-pymex --no-pyme-build --matplotlib-numpy-latest --setuptools-latest --use-git

    # build pyme with meson
    cd build-test-py3.11-conda_meson/python-microscopy-master
	conda activate test-pyme-3.11-conda_meson
	pip install build # conda tries to install some 0.x version of build which fails
	# just saw on the "build" page (https://pypi.org/project/build/): "on conda-forge, this package is called python-build"
	conda install meson meson-python
	export ARCHFLAGS="-arch arm64" # we should be able to use platform.uname().machine to predict the arch
	# how do we set env vars when running the build via subprocess, probably using a shell?
	pip install --no-deps --no-build-isolation --editable . # largely an equivalent of python setup.py develop
	pip install build # is this needed?
	
	# now add PYME-extra
	conda deactivate
	cd ../..
	python mk_extra_stuff.py --python=3.11 --suffix=_meson --use-git --xtra-sets PYME-extra

	# reactivate the new env
	conda activate test-pyme-3.11-conda_meson

## Notes

- currently building seems to require a full PYME git install in one of the meson build steps; need to check if this a firm requirement or can be worked around
