import json
from subprocess import run
import re
import sys
import logging

logger = logging.getLogger(__name__)

def conda_list(environment):
    proc = run(["conda", "list", "--json", "--name", environment],
               text=True, capture_output=True)
    return json.loads(proc.stdout)

def conda_envs():
    proc = run(["conda", "env", "list"],
               text=True, capture_output=True)
    lines = proc.stdout.split("\n")
    entry = re.compile("(\S+)\s+[*]*\s*(\S+)")
    envs = {}
    for line in lines:
        if line.startswith('#'):
            continue
        if entry.match(line):
            key,item = entry.match(line).groups()
            envs[key] = item

    return envs

def conda_create(environment,python='3.7', channels = None):
    if environment in conda_envs():
        raise RuntimeError('environment "%s" already exists' % (environment))
    packages = ["python=%s" % python]
    channelspecs = []
    for chan in channels:
        channelspecs += ["--channel", chan]
    cmd = ["conda", "create", "--json", "-y", "--name", environment] + channelspecs + packages
    logger.info("command is '%s'" % cmd)
    proc = run(cmd, text=True, capture_output=True)
    return proc.stdout

def conda_remove(environment):
     proc = run(["conda", "remove", "-n", environment, "-y", "--all"], text=True, capture_output=True)
     return proc.stdout

# use channels as needed
def conda_install(environment, packages, channels = None):
    channelspecs = []
    for chan in channels:
        channelspecs += ["--channel", chan]
    cmd = ["conda", "install", "--quiet", "--yes", "--name", environment] + channelspecs + list(packages)
    logger.info("command arg list is '%s'" % cmd)
    proc = run(cmd, text=True, capture_output=True)
    return proc.stdout

from urllib.parse import urljoin
def repo_url(repo,branch='master'):
    snapshot_path = '%s/archive/refs/heads/%s.zip' % (repo,branch)
    github_prefix = 'https://github.com/'
    repo_url = urljoin(github_prefix, snapshot_path)
    return repo_url

def unpack_snapshot(snapshot_file,target_dir):
    import shutil
    shutil.unpack_archive(snapshot_file,target_dir)

def repobasename(repo):
    return repo.split('/')[-1]
    
def download_repo(repo, target_dir):
    import requests
    import pathlib

    url = repo_url(repo)

    downloaded_file = pathlib.Path(target_dir) / ("%s.zip" % repobasename(repo))
    downloaded_file.write_bytes(requests.get(url).content)


def repo_dirname(repo,branch='master'):
    return repobasename(repo) + '-%s' % branch


def mk_compound_cmd(*cmds):
    from sys import platform
    if platform == "linux" or platform == "linux2":
        sep = ' ; '
    elif platform == "darwin":
        sep = ' ; '
    elif platform == "win32":
        sep = ' && '

    return sep.join(cmds)

# currently only for mac/linux
# modify for windows
def run_cmd_in_environment(cmd, environment):
    compoundcmd = mk_compound_cmd("conda activate %s" % (environment), cmd)
    logger.info("command is %s" % compoundcmd)
    proc = run(compoundcmd, text=True, capture_output=True, shell=True)
    return proc.stdout

def pip_install(environment, packages):
    args = ['python', '-m', 'pip', 'install'] + list(packages)
    return run_cmd_in_environment(' '.join(args),environment)
