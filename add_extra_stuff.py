import condacmds as cmds
from condacmds import PymeBuild
#from condacmds import download_pyme_extra, download_pyme, build_pyme_extra, build_pyme, pyme_extra_install_plugins
from pathlib import Path
import logging

# this will become a replacement for mk_extra_stuff and will be based on reading the build settings
# from a previous pyme env build run

# list of known package sets
# potentially something about pyarrow (for pandas)

extrapackages = {
    'notebooks' : {'conda': 'notebook ipympl nb_conda_kernels'.split()},
    'notebooks-jupyterlab' : {'conda': 'ipympl jupyterlab nb_conda_kernels'.split()},
    # pymecompress is supplied from channel david_baddeley but that should already be in the list of channels
    'pymecompress' : {'conda': ['pymecompress']}, # pip or source build on win requires mingW compiler etc
    'seaborne': {'conda': 'seaborn openpyxl'.split()}, # for latest PYME-extra; we add openpyxl for excel IO
    'alphashape': {'conda': ['alphashape']}, # PYME-extra: not absolutely required but potentially useful; convexHull is used as fallback
    }

def install_pymenf(ziplocation,build_dir,environment):
    # we need a zip file with pymenf option for installation
    # unpack into suitable place and then build
    # and register recipe modules
    zippath = Path(ziplocation)
    if not zippath.exists():
        raise RuntimeError("cannot find pymenf zip archive '%s', terminating..." % zippath)
    cmds.unpack_snapshot(zippath,build_dir)

    cmds.build_repo_generic(environment,'pymenf',build_dir,branch='master')
    cmds.repo_install_plugins_generic(environment,build_dir,'pymenf','master')

def install_pyme_siteconfig(build_dir,environment):
    # install the siteconfig repo
    # possibly into a dir outside the otherwise general build dir?
    pass

def check_xtra_packages(pack):
    if pack not in extrapackages:
            raise RuntimeError("asking to install meta-package %s which is not in the list of known metapackages %s" %
                               (pack, extrapackages.keys()))

def install_xtra_packages(environment,packages):
    for pack in packages:
        check_xtra_packages(pack)
        condapacks = extrapackages[pack].get('conda',None)
        if condapacks is not None and condapacks != '' and len(condapacks) != 0:
            result = cmds.conda_install(environment, condapacks, channels = ['david_baddeley','conda-forge'])
            logging.info(result)
        pippacks = extrapackages[pack].get('pip',None)
        if pippacks is not None and pippacks != '' and len(pippacks) != 0:
            result = cmds.pip_install(environment, pippacks)
            logging.info(result)

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-e','--environment',default=None,
                    help='name for the environment to which stuff should be added, must exist')
parser.add_argument('--dry-run',action="store_true",
                    help='just process options but do not run any commands')
parser.add_argument('-x','--xtra-packages', action="extend", nargs="+", type=str,
                    help='extra packages to install into the new environment')
parser.add_argument('--pymenf',default=None,
                    help='location of pymenf repo snapshot zip archive')
parser.add_argument('--xtra-sets', action="extend", nargs="+", type=str,
                    help='extra package sets to install into the new environment')

args = parser.parse_args()

cmds.check_condaenv('base') # check we are running in the base environment
cmds.check_yaml_installed() # check yaml is available

conda_flags = '--override-channels -c conda-forge' # this is aimed at sticking to conda-forge and not mix with default channel etc

if args.environment is None:
    raise RuntimeError("You need to provide an environment name to add stuff to, none given")

if not cmds.check_env_registered(args.environment):
    raise RuntimeError("environment %s is not registered with PYME-test-env, aborting" % args.environment)

settings = cmds.read_env_settings(args.environment)
yaml_data = cmds.envfile(args.environment).read_text()
pb = PymeBuild.from_yaml(yaml_data)
print(pb)

if args.dry_run: # for now we stop here
    logging.info("dry run, aborting...")
    import sys
    sys.exit(0)
