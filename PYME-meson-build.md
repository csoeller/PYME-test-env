# Preliminary notes for meson based PYME build

## Current list of commands

Currently, the process is a little bit manual until sussed out more fully. We are working from David's short [build instructions](https://github.com/python-microscopy/python-microscopy/blob/master/BUILD.md).

Eventually, this will be folded into the main build command (`mk_pyme_env.py`).

	python mk_pyme_env.py --python=3.11 --suffix=_meson --no-pymex --no-pyme-build --matplotlib-numpy-latest --setuptools-latest --use-git

    # build pyme with meson
    cd build-test-py3.11-conda_meson/python-microscopy-master
	conda activate test-pyme-3.11-conda_meson
	pip install build # conda tries to install some 0.x version of build which fails
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
