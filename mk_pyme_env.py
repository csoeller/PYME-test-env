import condacmds as cmds
from pathlib import Path
import logging

# eventually we want to allow a mode 'git' to clone the full repository locally
def mk_git_url(repo):
    from urllib.parse import urljoin
    return urljoin('https://github.com/', "%s.git" % repo)

def clone_repo(repo,target_dir,branch='master'):
    import git

    repo = git.Repo.clone_from(mk_git_url(repo), # we need to define this function
                               target_dir,
                               branch=branch)

def download_pyme_extra(build_dir="build-test",branch='master',repo='csoeller/PYME-extra',mode='snapshot'):
    if mode == 'snapshot':
        cmds.download_repo(repo, build_dir,branch=branch)
        cmds.unpack_snapshot(Path(build_dir) / 'PYME-extra.zip', build_dir)
    elif mode =='git':
        target_dir = Path(build_dir) / cmds.repo_dirname(repo,branch=branch)
        clone_repo(repo,target_dir,branch=branch)
    else:
        raise RuntimeError("unknown mode '%s'" % mode)
    
def download_pyme(build_dir="build-test",branch='master',repo='python-microscopy/python-microscopy',mode='snapshot'):
    if mode == 'snapshot':
        cmds.download_repo(repo, build_dir,branch=branch)
        cmds.unpack_snapshot(Path(build_dir) / 'python-microscopy.zip', build_dir)
    elif mode =='git':
        target_dir = Path(build_dir) / cmds.repo_dirname(repo,branch=branch)
        clone_repo(repo,target_dir,branch=branch)
    else:
        raise RuntimeError("unknown mode '%s'" % mode)

def build_pyme(environment,build_dir="build-test",repo='python-microscopy/python-microscopy',branch='master'):
    ret = cmds.build_repo(repo,environment,build_dir=build_dir,branch=branch)
    logging.info("building PYME...")
    logging.info(ret)

def build_pyme_extra(environment,build_dir="build-test",repo='csoeller/PYME-extra',branch='master'):
    ret = cmds.build_repo(repo,environment,build_dir=build_dir,branch=branch)
    logging.info("building PYME-extra...")
    logging.info(ret)

def pyme_extra_install_plugins(environment,build_dir="build-test",repo='csoeller/PYME-extra',branch='master'):
    ret = cmds.repo_install_plugins(repo,environment,build_dir=build_dir,branch=branch)
    logging.info("installing PYME-extra plugins...")
    logging.info(ret)

# first attempt at a central package list
# not yet used 
Packages = {
    'with_pyme_depends' : {
        'packages' : 'matplotlib<=3.6 pyme-depends'.split()
    },
    'no_pyme_depends' : {
        'packagelists_mac' : {
            'conda' : [
                'scipy numpy "libblas=*=*accelerate"'.split(),
                ('matplotlib<=3.6 pytables pyopengl jinja2 cython pip requests pyyaml' +
                 ' psutil pandas scikit-image scikit-learn sphinx toposort pybind11').split(),
                'traits traitsui==7.1.0 pyface==7.1.0'.split(),
                'python.app'.split(),
            ],
            'pip': ['wxpython']},
        'packagelists_win' : {
            'conda': [
                'scipy numpy'.split(),
                ('matplotlib<=3.6 pytables pyopengl jinja2 cython pip requests pyyaml' +
                 ' psutil pandas scikit-image scikit-learn sphinx toposort pybind11').split(),
                'traits traitsui==7.1.0 pyface==7.1.0'.split(),
                'pywin32'.split(),
            ],
            'pip': ['wxpython']}        
    }
}

# 0. some basic setup/parameter choices via command line arguments

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--python',default='3.9',
                    help='specify the python version for the new environment')
parser.add_argument('--buildstem',default='build-test',
                    help='stem for the name of the build directory')
parser.add_argument('-c','--condacmd',default='conda',choices=['conda','mamba'],
                    help='conda command, should be one of conda or mamba')
parser.add_argument('-e','--environment',default=None,
                    help='name for the new environment, autogenerated from other params by default')
parser.add_argument('--recipes',action="store_true",
                    help='install the included customrecipes into the PYME config directory')
parser.add_argument('--pyme-repo',default='python-microscopy/python-microscopy',
                    help='github repository name of python-microscopy; defaults to python-microscopy/python-microscopy')
parser.add_argument('--pyme-branch',default='master',
                    help='branch of pyme to use in build; defaults to master')
parser.add_argument('--pymex-repo',default='csoeller/PYME-extra',
                    help='github repository name of PYME-extra; defaults to csoeller/PYME-extra')
parser.add_argument('--pymex-branch',default='master',
                    help='branch of PYME-extra to use in build; defaults to master')
parser.add_argument('--no-pymex',action="store_true",
                    help='omit downloading and installing PYME-extra')
parser.add_argument('--no-pyme-depends',action="store_true",
                    help='install from package list rather than using pyme-depends')
parser.add_argument('--use-git',action="store_true",
                    help='clone git repo locally rather than just downloading snapshot')


### Note
### we may want to add, will enforce from conda-forge over default channel (I think)
# conda config --set channel_priority strict
# we should be able to provide this as an option, according to https://docs.conda.io/projects/conda/en/latest/commands/install.html:
#  --strict-channel-priority
### Check how to check, verify and unset


# other possible arguments to enable
# --pyme-branch: pick a branch other than the default 'master' branch
# --pyme-extra-branch: pick a branch other than the default 'master' branch
# --build_dir: specify full build directory name (e.g. for a more permanent install)
# potentially add jupyter notebook option
# potentially add R option (+R notebooks?)
# potentially allow cloning the whole github repos with a command line switch

args = parser.parse_args()

# # this makes methods/attributes for the standard parameters available
# # also does any setup stuff, e.g. create build_dir, setup logging etc
pbld = cmds.PymeBuild(pythonver=args.python,
                      build_dir=args.buildstem,
                      condacmd=args.condacmd,
                      environment=args.environment,
                      with_pyme_depends=not args.no_pyme_depends,
                      with_pymex=not args.no_pymex,
                      with_recipes=args.recipes,
                      pyme_repo=args.pyme_repo, pyme_branch=args.pyme_branch,
                      pymex_repo=args.pymex_repo, pymex_branch=args.pymex_branch,
                      use_git=args.use_git
                      )

environment = pbld.env
build_dir = pbld.build_dir

envs = cmds.conda_envs()

# 1. make test environment

if environment not in envs:
    cc = cmds.conda_create(environment, pbld.pythonver, channels=['conda-forge'])
    logging.info(cc)
else:
    print('environment %s already exists' % environment)
    answer = input("Continue?")
    if answer.lower() not in ["y","yes"]:
        print("aborting...")
        import sys
        sys.exit(0)

# just a quick check that we get the expected python version and can invoke it ok
cc = cmds.run_cmd_in_environment('python -V',environment,check=True)
logging.info("got python version info: %s" % cc)

# 2. build/install pyme and dependencies

# pyme-depends
# current constraints:
# matplotlib<=3.6: matplotlib 3.7.X onwards backend_wx.cursord dictionaries are removed;
#                 3.8.X removes error_msg_wx function in backend_wx;
#                 both are used in PYME/DSView/modules/graphViewPanel.py
#                 this one needs enforcing both with pyme-depends and full package based installs (as on arm64)
# traitsui==7.1.0 pyface==7.1.0: what is the issue?
#                 this one needs enforcing only with full package based installs (as on arm64);
#                 probably implicitly established via pyme-depends based install
import platform
from packaging import version # should be available in the base install; otherwise we may need "# conda/pip install packaging"
prepy3_10 = version.parse(pbld.pythonver) < version.parse("3.10")
if platform.machine() != 'arm64' and prepy3_10 and pbld.with_pyme_depends:
    # the initial matplotlib pinning should ensure we do not get a too recent version 
    packages = 'matplotlib<=3.6 pyme-depends'.split()
    
    result = cmds.conda_install(environment, packages, channels = ['conda-forge','david_baddeley'])
    logging.info(result)
else:
    # NOTE: mac on arm has no pre-built pyme-depends - we need to install all the required packages "manually" (in a fashion)
    # start off with numpy/scipy
    # the "libblas=*=*accelerate" arguments according to a number of sites, e.g.
    #   - https://github.com/joblib/threadpoolctl/issues/135
    #   - https://github.com/conda-forge/numpy-feedstock/issues/303

    # note docs on blas selection: https://conda-forge.org/docs/maintainer/knowledge_base.html#switching-blas-implementation
    # possible options
    # conda install "libblas=*=*mkl"
    # conda install "libblas=*=*openblas"
    # conda install "libblas=*=*blis"
    # conda install "libblas=*=*accelerate"
    # conda install "libblas=*=*netlib"

    if platform.system() == 'Darwin': # now selected for all macs
        package_stringset = 'scipy numpy "libblas=*=*accelerate"'.split()
    else:
        package_stringset = 'scipy numpy'.split()
    result = cmds.conda_install(environment, package_stringset, channels = ['conda-forge'])
    logging.info(result)

    if  platform.system() == 'Darwin': # now selected for all macs
        # next the main other dependecies
        package_sets = [('matplotlib<=3.6 pytables pyopengl jinja2 cython pip requests pyyaml' +
                         ' psutil pandas scikit-image scikit-learn sphinx toposort pybind11').split(),
                        'traits traitsui==7.1.0 pyface==7.1.0'.split(),
                        'python.app'.split(),
                        ]
    else:
        package_sets = [('matplotlib<=3.6 pytables pyopengl jinja2 cython pip requests pyyaml' +
                         ' psutil pandas scikit-image scikit-learn sphinx toposort pybind11').split(),
                        'traits traitsui==7.1.0 pyface==7.1.0'.split(),
                        'pywin32'.split(),
                        ]
 
    for packages in package_sets:
        result = cmds.conda_install(environment, packages, channels = ['conda-forge'])
        logging.info(result)

    # now pip install wx - the conda install was deemed not working at the time; may need to check again
    result = cmds.pip_install(environment, ['wxpython'])
    logging.info(result)

######################################
# note that we can get a windows error:
# error: could not create 'build\temp.win-amd64-cpython-310\Release\Users\soeller\src\PYME-test-env\b-py3.10-mamba\python-microscopy-python-310-compat\PYME\Analysis\points\traveling_salesperson':
#        The filename or extension is too long
# silly solution: move PYME-test-env repo close to root of disk and abbreviate build_directory name
#### There must be a better solution!!

if pbld.use_git:
    download_mode = 'git'
else:
    download_mode = 'snapshot'

download_pyme(build_dir=build_dir,repo=args.pyme_repo,branch=args.pyme_branch,mode=download_mode)
build_pyme(environment,build_dir=build_dir,repo=args.pyme_repo,branch=args.pyme_branch)

# this should fail if our PYME install failed
result = cmds.run_cmd_in_environment('python -c "import PYME.version; print(PYME.version.version)"',environment,check=True)
logging.info("Got PYME version %s" % result)

# 3. build/install pyme-extra
if pbld.with_pymex:
    # pyme-extra dependencies
    packages = 'statsmodels roifile'.split()

    result = cmds.conda_install(environment, packages, channels = ['conda-forge'])
    logging.info(result)

    # circle-fit is not available in a recent enough version via conda-forge
    packages = 'circle-fit'.split()
    result = cmds.pip_install(environment, packages)
    logging.info(result)

    download_pyme_extra(build_dir=build_dir,repo=args.pymex_repo,branch=args.pymex_branch,mode=download_mode)
    build_pyme_extra(environment,build_dir=build_dir,repo=args.pymex_repo,branch=args.pymex_branch)
    pyme_extra_install_plugins(environment,build_dir=build_dir,repo=args.pymex_repo,branch=args.pymex_branch)

if pbld.with_recipes:
    output = cmds.run_cmd_in_environment('python install_config_files.py',environment)
    logging.info(output)

# potentially here: test for succesfull pyme-extra install
