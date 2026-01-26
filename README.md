# PYME-test-env

We provide a small set of scripts and programmatic interfaces to `conda`/`mamba`/`pip` to fully programmatically carry out custom `pyme` + `pyme-extra` installs. Here `pyme` refers to the PYthon Microscopy Environment available at [python-microscopy](https://github.com/python-microscopy/python-microscopy) and the associated `PYME-extra` set of plugins for some extra functionality available via the [PYME-extra](https://github.com/csoeller/PYME-extra) repository. 

There are possibly neater ways to do such installs with a suitably crafted conda or pip package. For our purposes though we were after a set of tools to install **quickly** and **cheaply** a fully functional conda virtual environment with the latest `PYME` and `PYME-extra` from github. Additionally, it should be easy to switch the python version and some other aspects of the install. This makes building a "test install" pretty easy in one or two commands and then check if it works ok on most aspects PYME, if it does benefit from the more recent version of python, etc.

The `python-microscopy` build process has recently changed as PYME had to move to a new meson based build framework to stay compatible with most recent `Python` and `Numpy` packages. Within `PYME-test-env` new style vs old style builds should be auto-detected depending on the python-microscopy version a user is trying to build. Recent source will automatically trigger `PYME-test-env` to use the meson build system and issue all suitable commands under the hood.

We have used the scripts with windows and mac installs (including `arm64`) and the ability to rustle up a new fully functional environment mostly with a single command has already proved quite useful. Linux has not been included as a target as yet (for lack of current need) but it could probably be adapted to linux installs with relatively few changes.

We make extensive use of retrieving package dependencies from the `conda-forge` channel and this allows more recent python versions to be used for installation (tested currently from Python 3.10 up to Python 3.13, on macOS python-microscopy currently benefits from a small patch for high DPI displays which can be installed by selecting a branch from our PYME fork, see also recent [installation notes](Installation_notes.md)).

**Note**: some typical current commands are listed in the file [current-commands.md](current-commands.md).


## Installation notes

PYME builds with PYME-test-env occasionally run into issues with certain arguments (e.g. recent python versions). For recent issues and possible resolutions consult the [installation notes](Installation_notes.md). Be sure to check these notes when you run into any issues!

To run the scripts included with `PYME-test-env` a few packages are needed, such as `pyyaml` and `requests` plus some other dependencies (such as `conda` and others). Details are covered in the [section on installation](#installation) below.

## Synopsis

```shell
### we list a few "typical" commands and use cases here
### for suggested command sequences for an up-to-date install
### consult the file current-commands.md

# simplest possible install using pip packages from PyPi
python mk_pyme_env.py --python=3.12 --suffix=_pip --pip-pyme --pip-pymex

# install a test environment with python 3.10 using mamba for package resolution
python mk_pyme_env.py --python 3.10 -c mamba
	
# broadly similar but explictly name the created environment
python mk_pyme_env.py --python=3.11 -c mamba --environment pyme-py311-v1
	
# remove a test environment previously installed (see above)
python remove-pyme-environment.py pyme-py311-v1
	
# test with recent python and forked pyme to fix compatibility issue
# note double quotes in arguments for windows, single quotes cause issues!
python mk_pyme_env.py --python=3.12 --pyme-repo "csoeller/python-microscopy" \
    --pyme-branch=recipe-macos-dpi

```

## Installation


Most operations performed by the scripts are conda based. As such we need a conda based python installation on the machine as well as a few additional components as listed below.

### Required tools 

To start building test installs we need essentially 3 components (optionally a 4th) on the target machine:

   1. a working miniforge/miniconda installation (to handle the conda environments)
   2. a working copy of this repository
   3. a working compiler tool set (typically including a C compiler and linker etc)
   4. optionally, if you want to use git to download a cloned repo (`--use-git` option below), you need a working git install on the machine, see further below

First, we need a working conda/mamba install on that machine. On windows we currently recommend a [miniforge](https://github.com/conda-forge/miniforge) based install. On mac we have so far used a [miniconda](https://docs.conda.io/projects/miniconda/en/latest/) install, but a recent test with miniforge on an intel mac worked fine, too. `mamba` based installs require [miniforge](https://github.com/conda-forge/miniforge) and are recommended because of the much faster dependency resolution, particularly on windows. We describe below how to select between conda and mamba based installs.

### Required python packages in the base environment

We require `pyyaml` installed in the conda `base` environment, which can be added with

    conda install -n base pyyaml

In addition, the `requests` package is needed but that seems to be included by default as it is probably a dependency for `conda` itself. If you do get an error that the `requests` module cannot be imported please let us know as this would be a first.

We then just need a copy of this repository (`PYME-test-env`) unpacked into a directory on the target machine. No further installation process is required.

### Compiler tool set

Finally, we generally need a working compiler tool set. On windows we have instructions how to get that in this [document](https://github.com/csoeller/pyme-install-docs/blob/master/Installing-a-compiler-on-windows.md). On macs you can follow [this description](https://mac.install.guide/commandlinetools/4.html) on how to get the xcode command line tools on your system (if these are not already installed). 

    
## General approach

A brief high level overview of the approach is provided in this section. Detailed usage instructions are provided in paragraphs further below.

Using just a basic miniconda/minforge install (we use `conda` or `mamba` for most of the actual work under the hood) and this small repository + a working C compiler we build test installations of `PYME` and the plugin selection from `PYME-extra`. Most of the work is done by a script `mk_pyme_env.py` that attempts to build the new environment and accepts a few switches/options to control which versions of python are used etc.

We download a copy of the latest `PYME` and `PYME-extra` directly from github as part of the installation process, by default using the main branch. This can be changed with options to select specific branches. One can also request a full clone of the relevant repos using the `--use-git` option, see also below.

While originally intended to quickly whip up test installations these can also be turned into a production environment. In that case it is useful to name the environment explictly using a more descriptive name. On windows we provide a few launcher scripts that just need setting up of a couple of user level environment variables. With that an environment built via the scripts provided here can be set up for production work on a given machine. Details how to set this up are provided in a section below.

First thing after building a new environment is to check if all components installed ok or if an error was encountered when running the `mk_pyme_env.py` script.

If everything built ok it is recommended to use the installed PYME tools for a while and carry out a number of the usual visualisation/analysis tasks to see if everything works as intended. Particularly if newer versions of python or some of the associated pre-requisite modules were installed some bugs may become apparent when you use the installation a bit more.

## Usage

### Building a new pyme environment

The scripts need to be run in the directory where you have downloaded/unpacked the `PYME-test-env` dist. They need to be run while the conda `base` environment is activated (the scripts will check).

**IMPORTANT**: Make sure you are in the **base environment** when running any of the install commands below - typically indicated by the `(base)` prefix in your command window. Plenty of times I got errors and then realised I had already activated another environment which made the install fall over. *Note: the script now explictly checks if it is called from the base environment and if not prints an error to point out the issue.* In other words, this should now be relatively easy to troubleshoot.

**NOTE - Possible conda issues**: sometimes issues that show up as failed conda commands can result from outdated conda versions. This can be fixed from the base environment with a command like:

	conda update -n base conda
	
See also [How to use "conda update -n base conda" properly](https://stackoverflow.com/questions/70365296/how-to-use-conda-update-n-base-conda-properly).

**NOTE: Log file**: The build process will generate a log file in the build directory which can be inspected for errors if some part of the build appears to have failed. Please inspect the log file if you run into errors.

**NOTE: windows path length issues**: The paths in the subdirectories in the PYME package can become very long when everything is built (long string of subdirectories) and I have already hit some windows path length restrictions. The workaround is to clone the PYME-test-env repo into a short named folder near the top level, e.g. `C:\pte` and then cd into that directory and do everything from there. Windows is really silly at times...

### Simple Usage to create a pip based install

The perhaps simplest way to get a working PYME + PYME-extra install is a pip based install which has recently become possible. Details are described [here](https://github.com/csoeller/PYME-extra?tab=readme-ov-file#pip-install), it just takes a few commands to get a working install.

PYME-test-env enables a pip based install in a single command, e.g.

```
# simplest possible install using pip packages from PyPi
python mk_pyme_env.py --python=3.12 --suffix=_pip --pip-pyme --pip-pymex
```

This should work with Python 3.10 to 3.13 (pre 3.10 is not recommended as these Pythons have reached end-of-life). While the few commands could be directly typed it the one-liner supported by PYME-test-env makes exploring pip based installs with different python versions very quick and easy.

### General Usage

You first need to open a command window. On windows you need to start a "miniforge prompt" or "anaconda prompt", found somewhere in your start menu, sometimes in a submenu titled "miniconda" or similar depending if you used a miniforge or miniconda install.

On mac you open the terminal app.

You then need to cd into the directory where the PYME-test-env working copy resides.

Once in the directory, you can try to run the script to build the environment. Initially, try

	python mk_pyme_env.py -h

which should print the usage info, currently showing something like:

```
usage: mk_pyme_env.py [-h] [--python PYTHON] [--buildstem BUILDSTEM] [--suffix SUFFIX] [-c {conda,mamba}]
                      [-e ENVIRONMENT] [--recipes] [--pyme-repo PYME_REPO] [--pyme-branch PYME_BRANCH]
                      [--pymex-repo PYMEX_REPO] [--pymex-branch PYMEX_BRANCH] [--no-pymex] [--no-pyme-build]
                      [--no-pyme-depends] [--pyme-release PYME_RELEASE] [--pymex-release PYMEX_RELEASE] [--pip-pyme]
                      [--pip-pymex] [--use-git] [--no-strict-channel] [--dry-run]
                      [-x XTRA_PACKAGES [XTRA_PACKAGES ...]] [--matplotlib-numpy-latest] [--matplotlib-version-force]
                      [--setuptools-latest]

optional arguments:
  -h, --help            show this help message and exit
  --python PYTHON       specify the python version for the new environment
  --buildstem BUILDSTEM
                        stem for the name of the build directory
  --suffix SUFFIX       suffix appended to default environment and build_dir
  -c {conda,mamba}, --condacmd {conda,mamba}
                        conda command, should be one of conda or mamba
  -e ENVIRONMENT, --environment ENVIRONMENT
                        name for the new environment, autogenerated from other params by default
  --recipes             install the included customrecipes into the PYME config directory
  --pyme-repo PYME_REPO
                        github repository name of python-microscopy; defaults to python-microscopy/python-microscopy
  --pyme-branch PYME_BRANCH
                        branch of pyme to use in build; defaults to master
  --pymex-repo PYMEX_REPO
                        github repository name of PYME-extra; defaults to csoeller/PYME-extra
  --pymex-branch PYMEX_BRANCH
                        branch of PYME-extra to use in build; defaults to master
  --no-pymex            omit downloading and installing PYME-extra
  --no-pyme-build       omit building and installing PYME
  --no-pyme-depends     install from package list rather than using pyme-depends
  --pyme-release PYME_RELEASE
                        release tag for PYME release to build; mutually exclusive with --use-git option
  --pymex-release PYMEX_RELEASE
                        release tag for PYME-extra release to build; mutually exclusive with --use-git option
  --pip-pyme            install python-microscopy via pip and not from source
  --pip-pymex           install PYME-extra via pip and not from source
  --use-git             clone git repo locally rather than just downloading snapshot
  --no-strict-channel   enforce strict adherance to conda-forge channel
  --dry-run             just process options but do not run any commands
  -x XTRA_PACKAGES [XTRA_PACKAGES ...], --xtra-packages XTRA_PACKAGES [XTRA_PACKAGES ...]
                        extra packages to install into the new environment
```

Basic usage to build an environment might look like

	python mk_pyme_env.py --python 3.9 -c mamba

and generates output starting with

```
building PYME in env "test-pyme-3.9-mamba" with python ver 3.9 in "build-test-py3.9-mamba"...
```
This will take some time to complete the package downloading and building process.

If you want a setup for production use you might use (adapt the python version to your requirements):

	python mk_pyme_env.py --python 3.7 -c mamba -e pyme-py-3.7-v1 --recipes

which should build an environment named `pyme-py-3.7-v1` and install the included custom recipes for MINFLUX processing so that they can be selected from the MINFLUX menu of `PYMEVisualize` (AKA `visgui`).

**Note**: The pip-related options are illustrated [above](#simple-usage-to-create-a-pip-based-install).

```
  --pip-pyme            install python-microscopy via pip and not from source
  --pip-pymex           install PYME-extra via pip and not from source
```

### Using the new environment

If everything works ok, you can activate the new environment, e.g. something like (on your machine adapt the line below to the name of environment your command created):

	conda activate pyme-py-3.7-v1

and try some of the usual pyme commands.

For windows users, one can make this more simple by using the launchers we have included (for `visgui`, `dh5view` and `PYMEClusterOfOne`). For these to work one needs to set up a couple of environment variables so that conda/mamba are found and the correct environment is activated to execute the pyme apps from (see below).

### Downloading and building specific releases

In some circumstances you may want to download and build specific releases of `PYME` and `PYME-extra`. This can be achieved with the `--pyme-release` and `--pymex-release` options. If these options are not given a current snapshot of the `PYME` and `PYME-extra` repositories are downloaded and built.

The arguments to these options should be the release tag on github for the release in question, e.g.

    --pymex-release 25.11.29

Note that the release options will conflict with the `--use-git` option (explained below) if selected. The rationale is that you can choose the specific commit manually when you clone the repo using git.

### Use git to clone repos (useful to work on code in test environment)

When providing the `--use-git` option, PYME and PYME-extra will be cloned from github (rather than just downloading the head of the chosen branches). This is useful in several scenarios:

1. if you are looking at a more longterm installation and want to update regularly as PYME/PYME-extra get new commits
2. you might want to edit code in PYME/PYME-extra in that test environment and submit commits from those edits, e.g.
when working on compatibility with a more recent module version

There are a few smallish caveats to use this option.

1. The `GitPython` package needs to be installed in the base environment. The script tests if GitPython can be loaded and if not makes suggestions how to install it.
2. `GitPython` in turn requires a git executable in the path to actually run the required git commands under the hood.
3. On the mac there are various ways to obtain git, e.g. from the `macports` or `homebrew` packaging systems. On windows I have successfully used [git for windows](https://gitforwindows.org/), see also [git download](https://git-scm.com/download/win).

Example usage:

      python mk_pyme_env.py --python=3.10 --pyme-repo "csoeller/python-microscopy" --pyme-branch python-310-compat --use-git

#### Use alternative repo sources or branches

Docs on the following options:

```
 --pyme-repo PYME_REPO
                        github repository name of python-microscopy; defaults
                        to python-microscopy/python-microscopy
  --pyme-branch PYME_BRANCH
                        branch of pyme to use in build; defaults to master
  --pymex-repo PYMEX_REPO
                        github repository name of PYME-extra; defaults to
                        csoeller/PYME-extra
  --pymex-branch PYMEX_BRANCH
                        branch of PYME-extra to use in build; defaults to
                        master
```

Sometimes it is useful to specify a fork of the repo in question and/or select a specific branch to checkout (e.g. with specific fixes). This is readily achieved with the options shown above.

### Using the `--suffix` option

One can use the `--suffix SUFFIX` option, which will append the given `SUFFIX` to the generated environment and build directory names. This is useful if you already have a test environment for a given python version but want to build a second one to try some other aspect. Here is an example:

     python mk_pyme_env.py --python=3.10 --suffix="_1" [further options...]

This can be handy as you don't need to supply new environment names and build dir in some complex fashion.

### Launcher for Windows - Setting environment variables

The launchers are provided in the `launchers` subdirectory. You can use these with the windows `Open with...` dialog, for example, or try to drag files onto these launchers.

Before you can use the launchers though you need to set two environment variables:

   - `PYMEENV` - set to the name of the newly created environment you want to use, e.g. `pyme-py-3.7-v1`
   - `CONDAPATH` - set to the path to find the conda binaries

To figure out the correct value for `CONDAPATH` try (at a minforge/anaconda prompt):

	where conda

which, for example, prints on one of my systems:

	C:\Users\XXX\AppData\Local\miniforge3\condabin\conda.bat

The path to use is the directory in which conda was found, i.e. `C:\Users\XXX\AppData\Local\miniforge3\condabin`.

Please consult [this section](https://github.com/csoeller/pyme-install-docs/blob/master/PYMEAcquire/Overview-and-Upgrading.md#ways-to-set-the-pymeenv-environment-variable) in one of our other manuals on how to set the environment variables (the linked doc demonstrates it for the `PYMEENV` variable).

### Adding to an existing install

There is a separate command/script to add components to an existing install. Existing installs are identified by their (unique) conda environment name.
You get some help on this command by issuing it with the `-h` switch:

```
python mk_extra_stuff.py -h
```

which currently shows


```
usage: mk_extra_stuff.py [-h] [--list-xtra-sets] [-x XTRA_PACKAGES [XTRA_PACKAGES ...]] [--pymenf PYMENF]
                         [--xtra-sets XTRA_SETS [XTRA_SETS ...]] [--pymex-install] [--pymex-repo PYMEX_REPO]
                         [--pymex-branch PYMEX_BRANCH] [--pymex-release PYMEX_RELEASE] [--pip-pymex]
                         [--use-git] [--dry-run]
                         environment

positional arguments:
  environment           name of the existing conda environment that is to be added to - required argument

optional arguments:
  -h, --help            show this help message and exit
  --list-xtra-sets      list known extra package sets
  -x XTRA_PACKAGES [XTRA_PACKAGES ...], --xtra-packages XTRA_PACKAGES [XTRA_PACKAGES ...]
                        extra packages to install into the new environment
  --pymenf PYMENF       location of pymenf repo snapshot zip archive
  --xtra-sets XTRA_SETS [XTRA_SETS ...]
                        extra package sets to install into the new environment
  --pymex-install       install PYME extra (off by default)
  --pymex-repo PYMEX_REPO
                        github repository name of PYME-extra; defaults to csoeller/PYME-extra
  --pymex-branch PYMEX_BRANCH
                        branch of PYME-extra to use in build; defaults to master
  --pymex-release PYMEX_RELEASE
                        release tag for PYME-extra release to build; mutually exclusive with --use-git option
  --pip-pymex           install PYME-extra via pip and not from source
  --use-git             clone git repo locally rather than just downloading snapshot
  --dry-run             just process options but do not run any commands
```

Some typical uses are demonstrated in the file [current-commands.md](current-commands.md).

### Tidying up: removing an existing install

For convenience there is a separate command/script to remove an existing install. It will remove the conda environment and associated build directory. Existing installs are identified by their (unique) conda environment name.

You get some help on this command by issuing it with the `-h` switch:

```
python remove-pyme-environment.py -h
```

which currently shows


```
usage: remove-pyme-environment.py [-h] [--dry-run] environment

positional arguments:
  environment  name of the existing conda environment that is to be removed

optional arguments:
  -h, --help   show this help message and exit
  --dry-run    just process options but do not run any commands
```


## Issues

- We are currently not checking the success of some of the commands properly. This makes debugging issues a little harder
and we will consider making this more robust over time if we find the actual usage of this (somewhat experimental) project warrants it.
- We are using the `base` environment to run the installs from. One can argue with this as it may be preferable to leave `base` untouched
and we currently install a few packages, such as `pyyaml`, `git` and possibly more in future. It should be possible to make a specific
environment for `PYME-test-env` with a hardcoded name and install all dependencies into it. This way scripts can check for the name etc
and we can keep a pristine `base` but not sure how important a pristine `base` really is.
- The clean-up script `remove-pyme-environment.py` docs could be improved.
- The add-on install script `mk_extra_stuff.py` docs could be improved.

