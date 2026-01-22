import condacmds as cmds
import logging
from warnings import warn

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('environment',
                    help='name for the conda environment that is to be removed')
parser.add_argument('--python',default='3.9',
                    help='specify the python version for the new environment')
parser.add_argument('--buildstem',default='build-test',
                    help='stem for the name of the build directory')
parser.add_argument('-c','--condacmd',default='conda',choices=['conda','mamba'],
                    help='conda command, should be one of conda or mamba')
parser.add_argument('--suffix',default=None,
                    help='suffix appended to default environment and build_dir')
parser.add_argument('--dry-run',action="store_true",
                    help='just process options but do not run any commands')

args = parser.parse_args()

cmds.check_condaenv('base') # check we are running in the base environment
cmds.check_yaml_installed() # check yaml is available

if args.environment is None:
    raise RuntimeError("You need to provide an environment name to add stuff to, none given")

if not cmds.check_env_registered(args.environment):
    raise RuntimeError("environment %s is not registered with PYME-test-env, aborting" % args.environment)

pbld = cmds.pymebuild_from_env(args.environment)
if not pbld.essentials_exist():
    raise RuntimeError("issues with PYME environment %s:\n%s" % (args.environment,pbld.status_msg()))

print("removing environment %s with build dir %s" % (pbld.env,pbld.build_dir))

if args.dry_run:
    logging.info("dry run, aborting...")
    import sys
    sys.exit(0)

answer = input("Continue?")
if answer.lower() not in ["y","yes"]:
    print("aborting...")
    import sys
    sys.exit(1)

print("removing...")
print(cmds.conda_remove(pbld.env))

build_dir = pbld.build_dir

if build_dir.exists():
    print('removing build dir "%s"' % build_dir)
    answer = input("Continue?")
    if answer.lower() not in ["y","yes"]:
        print("aborting...")
        import sys
        sys.exit(1)

    import shutil
    shutil.rmtree(build_dir)

print("deregistering environment...")
pbld.deregister_environment()
print("environment %s was deregistered" % pbld.env)
