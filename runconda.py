import condacmds as cmds
from pathlib import Path
# Todo
#  need to add logging

import logging


# print(conda_list('conda-builds')[-1])
# nonex = conda_list('nonexisting')
# if 'exception_name' in nonex:
#     print("exception: %s" % nonex['exception_name'])

def download_pyme_extra():
    cmds.download_repo('csoeller/PYME-extra', "build-test")
    cmds.unpack_snapshot(Path("build-test") / 'PYME-extra.zip', "build-test")

def download_pyme():
    cmds.download_repo('python-microscopy/python-microscopy', "build-test")
    cmds.unpack_snapshot(Path("build-test") / 'python-microscopy.zip', "build-test")
    
Path("build-test").mkdir(exist_ok=True)

python='3.9'
environment='test-pyme-%s' % python

logging.basicConfig(filename=Path("build-test")/('build-%s.log' % environment),
                    encoding='utf-8', level=logging.DEBUG)

envs = cmds.conda_envs()
print(envs.keys())

if environment not in envs:
    cc = cmds.conda_create(environment, python, channels=['conda-forge'])
    logging.info(cc)


cc = cmds.run_cmd_in_environment('which python',environment)
logging.info(cc)

# pyme-depends
packages = 'pyme-depends'.split()
    
result = cmds.conda_install(environment, packages, channels = ['conda-forge','david-baddeley'])
logging.info(result)

# print(conda_remove(environment))

# create new environment
# install pyme-depends
# create new subdirectory for build
# download PYME snapshot
# attempt to install (as development install?)
# test install successful
# download PYME snapshot
# attempt to install (as development install?)
# test install successful

