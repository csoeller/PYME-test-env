# Useful command sequences for current installs

General assumptions:

- we build with the git option (`--use-git`), this requires a working git installed, especially on windows. This is explained in the docs.
- on windows we generally build with `mamba` using the minforge installation, this is also explained in the docs; on win `mamba` is significantly faster than using `conda`

## python 3.10


### win

```cmd
python mk_pyme_env.py --python=3.10 --suffix=_p -c mamba --use-git --pyme-repo "csoeller/python-microscopy"  --pyme-branch working-jan-2025
rem bombed at some stage of building pyme; went in and did another round of 'python setup.py develop' and that (apparently) worked
rem then picked up build with pyme-extra etc
python mk_extra_stuff.py --python=3.10 --suffix=_plugins -c mamba --use-git --xtra-sets PYME-extra
python mk_extra_stuff.py --python=3.10 --suffix=_plugins -c mamba --pymenf pymenf\pymenf-master.zip -x zarr
```

### mac
```
python mk_pyme_env.py --python=3.10 --suffix=_p --use-git
```

#### now deprecated

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
python mk_extra_stuff.py --python=3.11 --suffix=_1 --pymenf pymenf-master.zip # complete install on mac with pymenf
python mk_extra_stuff.py --python=3.11 --suffix=_1 --xtra-sets notebooks # and latest notebook code
```
#### now deprecated

We don't need the `working-jan-2025` anymore with all relevant PRs merged

```
python mk_pyme_env.py --python=3.11 --suffix=_1 --use-git --pyme-repo "csoeller/python-microscopy"  --pyme-branch working-jan-2025
python mk_extra_stuff.py --python=3.11 --suffix=_1 --pymenf pymenf-master.zip # complete install on mac with pymenf
python mk_extra_stuff.py --python=3.11 --suffix=_1 --xtra-sets notebooks # and latest notebook code
```

