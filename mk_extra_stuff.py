### extra stuff to install
### this script will deal with some extra things that you might like in a more permanent install
### this could include jupyter notebooks, jupyterlab, conda kernels for notebooks, etc

import condacmds as cmds
from pathlib import Path
import logging

import sys
commandline = " ".join(sys.argv)

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--python',default='3.9',
                    help='specify the python version for the new environment')
parser.add_argument('--buildstem',default='build-test',
                    help='stem for the name of the build directory')
parser.add_argument('--suffix',default=None,
                    help='suffix appended to default environment and build_dir')
parser.add_argument('-c','--condacmd',default='conda',choices=['conda','mamba'],
                    help='conda command, should be one of conda or mamba')
parser.add_argument('-e','--environment',default=None,
                    help='name for the new environment, autogenerated from other params by default')
parser.add_argument('--use-git',action="store_true",
                    help='clone git repo locally rather than just downloading snapshot')
parser.add_argument('--no-strict-channel',action="store_true",
                    help='enforce strict adherance to conda-forge channel')
parser.add_argument('--dry-run',action="store_true",
                    help='just process options but do not run any commands')
parser.add_argument('-x','--xtra-packages', action="extend", nargs="+", type=str,
                    help='extra packages to install into the new environment')
parser.add_argument('--pymenf',default=None,
                    help='location of pymenf repo snapshot zip archive')
parser.add_argument('--pymesite',default=None,
                    help='location where to build pyme site repo, default None, standard=build_dir, other=path_where _to_build')
parser.add_argument('--xtra-sets', action="extend", nargs="+", type=str,
                    help='extra package sets to install into the new environment')

args = parser.parse_args()

cmds.check_condaenv('base') # check we are running in the base environment

# some issue with PymeBuild class at the moment:
# - probably want different log file
# - build_dir must already exist
# - so does environment

# list of known package sets
extrapackages = {
    'notebooks' : {'conda': 'notebook ipympl nb_conda_kernels'.split()},
    'notebooks-jupyterlab' : {'conda': 'ipympl jupyterlab nb_conda_kernels'.split()},
    # pymecompress is supplied from channel david_baddeley but that should already be in the list of channels
    'pymecompress' : {'conda': ['pymecompress']}, # pip or source bild on win requires mingW compiler etc
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

conda_flags = '--override-channels -c conda-forge' # this is aimed at sticking to conda-forge and not mix with default channel etc

# while in the new env set a few channel options
# set env-specific channel options
# see also discussion in https://stackoverflow.com/questions/67202874/what-is-nb-conda-kernels-equivalent-for-python-3-9
# note: we may move these options into the main environment creating script
# conda config --env --set channel_priority strict
# conda config --env --add channels conda-forge

# # this makes methods/attributes for the standard parameters available
# # also does any setup stuff, e.g. create build_dir, setup logging etc
pbld = cmds.PymeBuild(pythonver=args.python,
                      build_dir=args.buildstem,
                      condacmd=args.condacmd,
                      environment=args.environment,
                      use_git=args.use_git,suffix=args.suffix,
                      strict_conda_forge_channel=not args.no_strict_channel,
                      dry_run=args.dry_run,xtra_packages=args.xtra_packages,
                      mk_build_dir=False,logfile="extra-stuff-%s.log" % args.environment)

environment = pbld.env
build_dir = pbld.build_dir

logging.info("Command called as\n")
logging.info(commandline + "\n")

if args.dry_run: # for now we stop here
    logging.info("dry run, aborting...")
    import sys
    sys.exit(0)

# need to check build_dir exists
if not build_dir.exists():
    raise RuntimeError("build dir '%s' does not exist, terminating..." % build_dir)
    
envs = cmds.conda_envs()
if environment not in envs:
    raise RuntimeError("environment '%s' does not exist, terminating..." % environment)

if args.pymenf is not None:
    install_pymenf(args.pymenf,build_dir,environment)

if args.xtra_sets is not None and len(args.xtra_sets) > 0:
    # check_xtra_packages(xset)
    install_xtra_packages(environment,args.xtra_sets)
