import condacmds as cmds
from pathlib import Path
import logging

# print(conda_list('conda-builds')[-1])
# nonex = conda_list('nonexisting')
# if 'exception_name' in nonex:
#     print("exception: %s" % nonex['exception_name'])

def download_pyme_extra(env_dir="build-test"):
    cmds.download_repo('csoeller/PYME-extra', env_dir)
    cmds.unpack_snapshot(Path(env_dir) / 'PYME-extra.zip', env_dir)

def download_pyme(env_dir="build-test"):
    cmds.download_repo('python-microscopy/python-microscopy', env_dir)
    cmds.unpack_snapshot(Path(env_dir) / 'python-microscopy.zip', env_dir)

def build_pyme(environment,env_dir="build-test"):
    ret = cmds.build_repo('python-microscopy/python-microscopy',environment,env_dir=env_dir)
    logging.info("building PYME...")
    logging.info(ret)

def build_pyme_extra(environment,env_dir="build-test"):
    ret = cmds.build_repo('csoeller/PYME-extra',environment,env_dir=env_dir)
    logging.info("building PYME-extra...")
    logging.info(ret)


def pyme_extra_install_plugins(environment,env_dir="build-test"):
    ret = cmds.repo_install_plugins('csoeller/PYME-extra',environment,env_dir=env_dir)
    logging.info("installing PYME-extra plugins...")
    logging.info(ret)

# 0. some basic setup/parameter choices (needs tyding up/streamlining)

# # this makes methods/attributes for the standard parameters available
# # also does any setup stuff, e.g. create build_dir, setup logging etc
pbld = cmds.PymeBuild(pythonver='3.9', build_dir='build-test', condacmd='conda')

environment = pbld.env
build_dir = pbld.build_dir

envs = cmds.conda_envs()

# 1. make test environment

if environment not in envs:
    cc = cmds.conda_create(environment, pbld.pythonver, channels=['conda-forge'])
    logging.info(cc)

cc = cmds.run_cmd_in_environment('python -V',environment)
logging.info("got python version info: %s" % cc)

# 2. build/install pyme and dependies

# pyme-depends
packages = 'pyme-depends'.split()
    
result = cmds.conda_install(environment, packages, channels = ['conda-forge','david_baddeley'])
logging.info(result)

download_pyme(env_dir=build_dir)
build_pyme(environment,env_dir=build_dir)

# potentially here: test for succesful pyme base install

# 3. build/install pyme-extra

# pyme-extra dependencies
packages = 'statsmodels roifile'.split()

result = cmds.conda_install(environment, packages, channels = ['conda-forge'])
logging.info(result)

# circle-fit is not available in a recent enough version via conda-forge
packages = 'circle-fit'.split()
result = cmds.pip_install(environment, packages)
logging.info(result)

download_pyme_extra(env_dir=build_dir)
build_pyme_extra(environment,env_dir=build_dir)
pyme_extra_install_plugins(environment,env_dir=build_dir)

# potentially here: test for succesful pyme-extra install

# print(conda_remove(environment))
