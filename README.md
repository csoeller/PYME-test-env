# PYME-test-env

We provide a small set of scripts and programmatic interfaces to `conda`/`mamba`/`pip` to fully programmatically carry out a custom `pyme` + `pyme-extra` install.

There are possibly neater ways to do this with conda or pip package builds but we were after a quick set of tools to install quickly a fully functional conda virtual environment with the latest `PYME` and `PYME-extra` from github. We have tested this with windows and mac installs (including `arm64`) and it has already proved quite useful.

We make some use of packages from the `conda-forge` channel and this appears to allow more recent python versions (tested so far up to python 3.9) to be used for installation. 

## Synopsis

	# install a test environment with python 3.9 using mamba for package resolution
	python mk_pyme_env.py --python 3.9 -c mamba
	
	# broadly similar but explictly name the created environment
	python mk_pyme_env.py --python=3.7 -c mamba --environment pyme-py37-v1
	
	# remove a test environment previously installed with a 3.10 python
	python remove-test-environment.py --python=3.10

## General approach

A brief high level overview of the approach is provided in this section. Detailed usage instructions are in paragraphs below.

Using just a basic miniconda/minforge install (we use `conda` or `mamba` for most of the actual work under the hood) and this small repository + a working C compiler we build test installations of `PYME` and the plugin selection from `PYME-extra`. Most of the work is done by a script `mk_pyme_env.py` that attempts to build the new environment and accepts a few switches/options to control which versions of python are used etc.

We download a copy of the latest `PYME` and `PYME-extra` directly from github as part of the installation process, by default using the main branch.

While originally intended to quickly whip up test installations these can also be turned into a production environment. In that case it is useful to name the environment explictly using a more descriptive name. On windows we provide a few launcher scripts that just need setting up of a couple of user level environment variables. With that a built environment can be set up for production work on a given machine. Details how to set this up are provided in a section below.

First thing after building a new environment is to check if all components installed ok or if an error was encountered when running the `mk_pyme_env.py` script.

If everything built ok it is recommended to use the installed PYME tools for a while and carry out a number of the usual visualisation/analysis tasks to see if everything works as intended. Particularly if newer versions of python or some of the associated pre-requisite modules were installed some bugs may become apparent when you use the installation a bit more.

### Requirements before you can start an install

To start building test installs we need essentially 3 ingredients on the target machine:

   1. a working miniforge/miniconda installation
   2. a working copy of this repo
   3. a working compiler tool set (typically including a C compiler and linker etc)

First, we need a working conda/mamba install on that machine. On windows we currently recommend a [miniforge](https://github.com/conda-forge/miniforge) based install. On mac we have so far used a [miniconda](https://docs.conda.io/projects/miniconda/en/latest/) install, but a recent test with miniforge on an intel mac worked fine, too. `mamba` based installs require [miniforge](https://github.com/conda-forge/miniforge) and are recommended because of the much faster dependency resolution, particularly on windows. We describe below how to select between conda and mamba based installs.

We then just need a copy of this repo (`PYME-test-env`) unpacked into a directory on the target machine. No further installation process is required.

Finally, we need a working compiler tool set. On windows we have instructions how to get that in this [document](https://github.com/csoeller/pyme-install-docs/blob/master/Installing-a-compiler-on-windows.md).

On macs you can follow [this description](https://mac.install.guide/commandlinetools/4.html) on how to get just the xcode command line tools on your system. 

### Building the environment

You first need to open a command window. On windows you need to start a "miniforge prompt" or "anaconda prompt", depending if you used a miniforge or miniconda install.

On mac you open the terminal app.

You then need to cd into the directory where the PYME-test-env working copy resides.

Once in the directory, you can try to run the script to build the environment. Initially, try

	python mk_pyme_env.py -h

which should print the usage info, currently showing something like:

```
usage: mk_pyme_env.py [-h] [--python PYTHON] [--buildstem BUILDSTEM]
                      [-c {conda,mamba}] [-e ENVIRONMENT] [--recipes]

options:
  -h, --help            show this help message and exit
  --python PYTHON       specify the python version for the new environment
  --buildstem BUILDSTEM
                        stem for the name of the build directory
  -c {conda,mamba}, --condacmd {conda,mamba}
                        conda command, should be one of conda or mamba
  -e ENVIRONMENT, --environment ENVIRONMENT
                        name for the new environment, autogenerated from other
                        params by default
  --recipes             install the included customrecipes into the PYME
                        config directory
```

Basic usage build an environment might look like

	python mk_pyme_env.py --python 3.9 -c mamba

and generates output starting with

```
building PYME in env "test-pyme-3.9-mamba" with python ver 3.9 in "build-test-py3.9-mamba"
```
This will take some time to complete the package downloading and building process.

If you want a setup for production use you might use (adapt the python version to your requirements):

	python mk_pyme_env.py --python 3.7 -c mamba -e pyme-py-3.7-v1 --recipes

which should build an environment named `pyme-py-3.7-v1` and install the included custom recipes for MINFLUX processing so that they can be selected from the MINFLUX menu of `PYMEVisualize` (AKA `visgui`).

The build process will generate a log file in the build directory which can be inspected for errors if some part of the build appears to have failed.

If everything works ok, you can activate the new environment, something like

	conda activate pyme-py-3.7-v1

and try some of the usual pyme commands.

For windows users, one can make this more simple by using the launchers we have included (for `visgui`, `dh5view` and `PYMEClusterOfOne`). For these to work one needs to set up a couple of environment variables so that conda/mamba are found and the correct environment is activated to execute the pyme apps from (see below).

### Set environment variables for windows

The launchers are provided in the `launchers` subdirectory. You can use this with the windows `Open with...` dialog, for example, or try to drag files onto these launchers.

Before you can use the launchers though you need to set two environment variables:

   - `PYMEENV` - set to the name of the newly created environment you want to use, e.g. `pyme-py-3.7-v1`
   - `CONDAPATH` - set to the path to find the conda binaries

To figure out the correct value for `CONDAPATH` try

	where conda

which, for example, prints on one of my systems:

	C:\Users\soeller\AppData\Local\miniforge3\condabin\conda.bat

The path to use is the directory in which conda was found, i.e. `C:\Users\soeller\AppData\Local\miniforge3\condabin`.

Please consult [this section](https://github.com/csoeller/pyme-install-docs/blob/master/PYMEAcquire/Overview-and-Upgrading.md#ways-to-set-the-pymeenv-environment-variable) in one of our other manuals on how to set the environment variables (the linked doc demonstrates it for the `PYMEENV` variable).

### Tidying up: removing test environments / builds

For convenience in removing test environments and build directories we have a little script that is invoked with:

	python remove-test-environment.py ...

The idea is to use the same options used to create the environment and it should figure out which environment to remove and where the build directory is. We'll add more docs on this script if needed/requested.