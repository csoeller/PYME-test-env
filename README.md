# PYME-test-env

We provide a small set of scripts and programmatic interfaces to `conda`/`mamba`/`pip` to fully programmatically carry out a custom `pyme` + `pyme-extra` install.

There are probably neater ways to do this with conda or pip package builds but we were after a quick set of tools to install quickly a fully functional conda virtual environment with the latest `PYME` and `PYME-extra` from github. We have tested this with windows and mac installs (including `arm64`) and it has already proved quite useful.

We make some use of packages from the `conda-forge` channel and this appears to allow more recent python versions (tested so far up to python 3.9) to be used for installation. 

## Synopsis

   - show a few example invocations
   - ...

## How to use it

We merely need to get a working copy of this repository onto the target machine. This just needs to be somewhere on that machine and no installation of the code is necessary.

You also need a working conda/mamba install on that machine. On windows we currently recommend a miniforge based install. On mac we have so far used a miniconda install.

You then open a command window (terminal on mac, "miniforge prompt" or "anaconda prompt" on windows). You cd into the directory where the PYME-test-env working copy resides.

You then go through the remaining steps:

1. build the environment with a command like `python mk_pyme_env.py [options...]`
2. optionally install some customrecipes for `PYME` (make this a command)
3. on windows, optionally set a few environment variables to be able to use the installed PYME environment via a set of included launcher batch files

First thing is to check if all components installed ok or if an error was encountered in step 1.

If everything built ok it is recommended to use the installed PYME tools for a while and a number of the usual visualisation/analysis tasks and see if everything works as intended. Particularly if newer versions of python or some of the associated pre-requisite modules were installed some bugs may become apparent when you use the installation a bit more.

On windows step 3 allows you to use the new test environment for some production work and see how it goes.

Step 2 makes a couple of customrecipes available that can be useful, for example, when you work with MINFLUX data.

### Requirements before you can start an install

   - C compiler
   - minforge/miniconda

### Building the environment

   - `mk_pyme_env.py` script
   - command line options
   - error checking

### Set environment variables for windows

   - launchers
   - associating extensions with these launchers

### Tidying up: removing test environments / builds

   - `remove-test-environment.py` script