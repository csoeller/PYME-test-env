### extra stuff to install
### this script will deal with some extra things that you might like in a more permanent install
### this could include jupyter notebooks, jupyterlab, conda kernels for notebooks, etc

import condacmds as cmds
from pathlib import Path
import logging

# list of known package sets
extrapackages = {
    'notebooks' : {'conda': 'notebook ipympl nb_conda_kernels'.split()},
    'notebooks-jupyterlab' : {'conda': 'ipympl jupyterlab nb_conda_kernels'.split()},
    # pymecompress is supplied from channel david_baddeley but that should already be in the list of channels
    'pymecompress' : {'conda': ['pymecompress']}, # pip or source bild on win requires mingW compiler etc
    'seaborn': {'conda': 'seaborn openpyxl'.split()},
    'alphashape': {'pip': ['alphashape']},
    }

def install_pymenf(ziplocation,build_dir,environment):
    # we need a zip file with pymenf option for installation
    # unpack into suitable place and then build
    # and register recipe modules

    pymenf_src = cmds.SourceInfo(environment,build_dir,
                 local_file=ziplocation,
                 install_test_file='meson.build',
                 post_install_cmd={
                     'new' : 'python install_plugins.py', # this is fine because we do not work with pip at this stage
                     'old' : 'python install_plugins.py',
                 },)
    
    pymenf_src.download() # the download is here really just an unpack of the zip and checking
    pymenf_src.build_and_install()
    pymenf_src.postinstall()
    
def install_pyme_siteconfig(build_dir,environment):
    # install the siteconfig repo
    # possibly into a dir outside the otherwise general build dir?
    pass

def install_pyme_extra(pbld):
    # build/install pyme-extra
    # pyme-extra dependencies
    from packagesettings import Pymex_conda_packages, Pymex_pip_packages

    if not pbld.pip_install:
        result = cmds.conda_install(pbld.env, Pymex_conda_packages, channels = ['conda-forge'])
        logging.info(result)

        result = cmds.pip_install(pbld.env, Pymex_pip_packages)
        logging.info(result)

    pbld.pymex_src.download()
    pbld.pymex_src.build_and_install()
    pbld.pymex_src.postinstall()

def check_xtra_packages(pack):
    if pack not in extrapackages:
            raise RuntimeError("asking to install meta-package %s which is not in the list of known metapackages %s" %
                               (pack, extrapackages.keys()))
def list_xtra_sets():
    import pprint
    print("known extra package sets...")
    pprint.pprint(extrapackages)

def install_xtra_packages(pbld,packages):
    environment = pbld.env
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

import sys
commandline = " ".join(sys.argv)

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('environment',default=None,
                    help='name for the conda environment that is to be added to - required argument')
parser.add_argument('--list-xtra-sets', action="store_true",
                    help='list known extra package sets')
parser.add_argument('-x','--xtra-packages', action="extend", nargs="+", type=str,
                    help='extra packages to install into the new environment')
parser.add_argument('--pymenf',default=None,
                    help='location of pymenf repo snapshot zip archive')
parser.add_argument('--xtra-sets', action="extend", nargs="+", type=str,
                    help='extra package sets to install into the new environment')
parser.add_argument('--pymex-install',action="store_true",
                    help='install PYME extra (off by default)')
parser.add_argument('--pymex-repo',default='csoeller/PYME-extra',
                    help='github repository name of PYME-extra; defaults to csoeller/PYME-extra')
parser.add_argument('--pymex-branch',default='master',
                    help='branch of PYME-extra to use in build; defaults to master')
parser.add_argument('--pymex-release',default=None,
                    help='release tag for PYME-extra release to build; mutually exclusive with --use-git option')
parser.add_argument('--pip-pymex',action="store_true",
                    help='install PYME-extra via pip and not from source')
parser.add_argument('--use-git',action="store_true",
                    help='clone git repo locally rather than just downloading snapshot')
parser.add_argument('--dry-run',action="store_true",
                    help='just process options but do not run any commands')

args = parser.parse_args()

# some issue with PymeBuild class at the moment:
# - probably want different log file
# - build_dir must already exist
# - so does environment

cmds.check_condaenv('base') # check we are running in the base environment
cmds.check_yaml_installed() # check yaml is available

if args.environment is None:
    raise RuntimeError("You need to provide an environment name to add stuff to, none given")

if not cmds.check_env_registered(args.environment):
    raise RuntimeError("environment %s is not registered with PYME-test-env, aborting" % args.environment)

pbld = cmds.pymebuild_from_env(args.environment)
if not pbld.essentials_exist():
    raise RuntimeError("issues with PYME environment %s:\n%s" % (args.environment,pbld.status_msg()))
pbld.dry_run = args.dry_run or args.list_xtra_sets # in those two cases do not create logfile etc

environment = pbld.env
build_dir = pbld.build_dir

if args.pymex_install:
    pbld.pymex_repo = args.pymex_repo
    pbld.pymex_branch = args.pymex_branch
    pbld.pymex_release = args.pymex_release
    pbld.pymex_pip = args.pip_pymex
    pbld.use_git = args.use_git
    pbld.mk_src_attributes()

pbld.setup_logging(logfile="extra-stuff-$environment$.log")

# check consistency of some of the arg choices
pbld.check_consistency()

# # this makes methods/attributes for the standard parameters available
# # also does any setup stuff, e.g. create build_dir, setup logging etc
# pbld = cmds.PymeBuild(pythonver=args.python,
#                       build_dir=args.buildstem,
#                       condacmd=args.condacmd,
#                       environment=args.environment,
#                       use_git=args.use_git,suffix=args.suffix,
#                       pymex_repo=args.pymex_repo, pymex_branch=args.pymex_branch,
#                       pymex_release=args.pymex_release,pymex_pip=args.pip_pymex,
#                       strict_conda_forge_channel=not args.no_strict_channel,
#                       dry_run=dry_run,xtra_packages=args.xtra_packages,
#                       mk_build_dir=False,logfile="extra-stuff-$environment$.log")

logging.info("Command called as\n")
logging.info(commandline + "\n")

if args.list_xtra_sets:
    list_xtra_sets()
    import sys
    sys.exit(0)
    
if args.dry_run: # for now we stop here
    logging.info("dry run, aborting...")
    import sys
    sys.exit(0)

if args.pymenf is not None:
    install_pymenf(args.pymenf,build_dir,environment)

if args.pymex_install:
    install_pyme_extra(pbld)

if args.xtra_sets is not None and len(args.xtra_sets) > 0:
    # check_xtra_packages(xset)
    install_xtra_packages(pbld,args.xtra_sets)

# 5. any extra packages requested
if pbld.xtra_packages is not None and len(pbld.xtra_packages) > 0:
    result = cmds.conda_install(environment, pbld.xtra_packages, channels = ['conda-forge'])
    logging.info(result)
