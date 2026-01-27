# Useful command sequences for current installs

General assumptions:

- we often build with the git option (`--use-git`), this requires a working git installed, especially on windows. This is explained in the docs.
- on windows we generally build with `mamba` using the miniforge installation, this is also explained in the docs; on win `mamba` is significantly faster than using `conda`
- the `--suffix` option can generally be set to something convenient to tag the created environment so you know what is was made for etc
- some commands mention the `pymenf` package/option; this is part of a non-free package and lines mentioning this can be safely ignored by those not having access

## install using pip install from PyPI

This one just makes a new environment with the chosen Python version and then installs PYME and PYME-extra from PyPi, no actual build required. Easiest install by far.

```shell
python mk_pyme_env.py --python=3.12 --suffix=_pip --pip-pyme --pip-pymex
```

## install with Python 3.13

Currently new type installs (meson builds with newer matplotlib etc) need a `PYME` fix that is as yet only available via our fork. This seems to only affect mac installations and using high DPI displays.

```shell
python mk_pyme_env.py --python 3.13 -c conda --pyme-repo=csoeller/python-microscopy --pyme-branch=recipe-macos-dpi
```

## install from latest snapshots

```shell
python mk_pyme_env.py --python 3.11 -c conda --suffix=_sn --pyme-repo=csoeller/python-microscopy --pyme-branch=recipe-macos-dpi
```

## install with explicitly released versions

This one we use with publications to install from specific releases.

```shell
python mk_pyme_env.py --python 3.10 -e test-pyme-natcomm25 --pymex-release 25.11.29 --pyme-release 25.05.16 --buildstem b-nctest --pyme-repo csoeller/python-microscopy
```

## full macOS install

The example is Python 3.11 based, it also installs the non-free components and everything needed to run a notebook server (i.e. being able to run Jupyter notebooks). 

```
python mk_pyme_env.py --python=3.11 --suffix=_t --use-git --pyme-repo=csoeller/python-microscopy --pyme-branch=recipe-macos-dpi
python add_extra_packs.py test-pyme-3.11-conda_t --pymenf pymenf-1.0.2.zip
python add_extra_packs.py test-pyme-3.11-conda_t --xtra-sets notebooks    
```

## below now deprecated / superceded

## python 3.10


### win

```cmd
python mk_pyme_env.py --python=3.10 --suffix=_1 -c mamba --use-git
rem bombed at some stage of building pyme; went in and did another round of 'python setup.py develop' and that (apparently) worked
rem then picked up build with pyme-extra etc
python add_extra_packs.py --python=3.10 --suffix=_1 -c mamba --use-git --xtra-sets PYME-extra
python add_extra_packs.py --python=3.10 --suffix=_1 -c mamba --pymenf pymenf\pymenf-master.zip -x zarr
```

### mac
```
python mk_pyme_env.py --python=3.10 --suffix=_1 --use-git
```

We don't need the `working-jan-2025` anymore with all relevant PRs merged

```
python mk_pyme_env.py --python=3.10 --suffix=_p --use-git --pyme-repo "csoeller/python-microscopy"  --pyme-branch working-jan-2025
```


## python 3.11

### win

```
python mk_pyme_env.py --python=3.11 --suffix=_1 -c mamba --use-git
```

#### now deprecated

We don't need the `working-jan-2025` anymore with all relevant PRs merged

```
python mk_pyme_env.py --python=3.11 --suffix=_1 -c mamba --use-git --pyme-repo "csoeller/python-microscopy"  --pyme-branch working-jan-2025
```

### mac

Complete install with pymenf (non-free, only available to some parties) and notebook server etc

```
python mk_pyme_env.py --python=3.11 --suffix=_1 --use-git
python add_extra_packs.py --python=3.11 --suffix=_1 --pymenf pymenf-master.zip # complete install on mac with pymenf
python add_extra_packs.py --python=3.11 --suffix=_1 --xtra-sets notebooks # and latest notebook code
```

#### for numpy 2.x testing

```
# we use the pretty adhoc --matplotlib-numpy-latest flag
python mk_pyme_env.py --python=3.11 --suffix=_2 --use-git --pyme-repo "csoeller/python-microscopy"  --pyme-branch numpy-2-compat --matplotlib-numpy-latest
```

#### now deprecated

We don't need the `working-jan-2025` anymore with all relevant PRs merged

```
python mk_pyme_env.py --python=3.11 --suffix=_1 --use-git --pyme-repo "csoeller/python-microscopy"  --pyme-branch working-jan-2025
python add_extra_packs.py --python=3.11 --suffix=_1 --pymenf pymenf-master.zip # complete install on mac with pymenf
python add_extra_packs.py --python=3.11 --suffix=_1 --xtra-sets notebooks # and latest notebook code
```

