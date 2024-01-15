import json
from subprocess import run
import re
import sys
import logging

condacmd = "conda"
logger = logging.getLogger(__name__)

def set_condacmd(cmd):
    global condacmd
    condacmd = cmd 

def conda_list(environment):
    global condacmd
    proc = run([condacmd, "list", "--json", "--name", environment],
               text=True, capture_output=True)
    return json.loads(proc.stdout)

def conda_envs():
    global condacmd
    proc = run([condacmd, "env", "list"],
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
    global condacmd
    if environment in conda_envs():
        raise RuntimeError('environment "%s" already exists' % (environment))
    packages = ["python=%s" % python]
    channelspecs = []
    for chan in channels:
        channelspecs += ["--channel", chan]
    cmd = [condacmd, "create", "--json", "-y", "--name", environment] + channelspecs + packages
    logger.info("command is '%s'" % cmd)
    proc = run(cmd, text=True, capture_output=True)
    return proc.stdout

def conda_remove(environment):
    global condacmd
    proc = run([condacmd, "remove", "-n", environment, "-y", "--all"], text=True, capture_output=True)
    return proc.stdout

# use channels as needed
def conda_install(environment, packages, channels = None):
    global condacmd
    channelspecs = []
    for chan in channels:
        channelspecs += ["--channel", chan]
    cmd = [condacmd, "install", "--quiet", "--yes", "--name", environment] + channelspecs + list(packages)
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

def repo_dir(repo,branch='master',env_dir="build-test"):
    import pathlib
    return pathlib.Path(env_dir) / repo_dirname(repo,branch=branch)

def repo_cmd(cmd,repo,environment,branch='master',env_dir="build-test"):
    # need to see if a relative path is enough
    repodir = repo_dir(repo,branch=branch,env_dir=env_dir)
    # we could make the install mode selectable
    result = run_cmd_in_environment(cmd, environment, cwd=repodir)
    return result

def build_repo(repo,environment,branch='master',env_dir="build-test"):    
    return repo_cmd("python setup.py develop",repo,environment,
                    branch=branch,env_dir=env_dir)

def repo_install_plugins(repo,environment,branch='master',env_dir="build-test"):
    return repo_cmd("python install_plugins.py",repo,environment,
                    branch=branch,env_dir=env_dir)

def mk_compound_cmd(*cmds):
    from sys import platform
    if platform == "linux" or platform == "linux2":
        sep = ' ; '
    elif platform == "darwin":
        sep = ' ; '
    elif platform == "win32":
        sep = ' && '

    return sep.join(cmds)

def run_cmd_in_environment(cmd, environment,cwd=None):
    global condacmd
    compoundcmd = mk_compound_cmd("%s activate %s" % (condacmd, environment), cmd)
    logger.info("command is %s" % compoundcmd)
    proc = run(compoundcmd, text=True, capture_output=True, shell=True, cwd=cwd)
    return proc.stdout

def pip_install(environment, packages):
    args = ['python', '-m', 'pip', 'install'] + list(packages)
    return run_cmd_in_environment(' '.join(args),environment)

import pathlib
import logging
class PymeBuild(object):
    def __init__(self,pythonver,build_dir='build-test',condacmd='conda'):
        self.pythonver = pythonver
        self.build_dir = pathlib.Path(build_dir)
        self.build_dir.mkdir(exist_ok=True)
        self.condacmd = condacmd
        set_condacmd(self.condacmd)
        self.env = 'test-pyme-%s' % self.pythonver

        # set up logging to file
        logging.basicConfig(
            filename=self.build_dir / ('build-%s.log' % self.env),
            encoding='utf-8',
            level=logging.DEBUG
        )

        # set up logging to console
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        # add the handler to the root logger
        logging.getLogger('').addHandler(console)

        logger.info('building PYME in env "%s" with python ver %s in "%s"' %
                    (self.env,self.pythonver,self.build_dir))
