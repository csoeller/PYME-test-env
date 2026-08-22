import condacmds as cmds
import argparse
import sys

parser = argparse.ArgumentParser("")
parser.add_argument("environment", help="name of conda environment to check")
args = parser.parse_args()

print("checking for environment %s" % args.environment)
envs = cmds.conda_envs()

if args.environment in envs:
    print("environment exists")
    sys.exit(0)
else:
    print("environment does not exist")
    sys.exit(1)

