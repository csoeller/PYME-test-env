import json
from subprocess import run
import re

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
    print("command is '%s'" % cmd)
    proc = run(cmd, text=True, capture_output=True)
    return proc.stdout

def conda_remove(environment):
     proc = run(["conda", "remove", "-n", environment, "-y", "--all"], text=True, capture_output=True)
     return proc.stdout

# use channels as needed
def conda_install(environment, *packages, channels = None):
    proc = run(["conda", "install", "--quiet", "--yes", "--name", environment] + packages,
               text=True, capture_output=True)
    return json.loads(proc.stdout)

from urllib.parse import urljoin
def repo_url(repo,branch='master'):
    snapshot_path = '%s/archive/refs/heads/%s.zip' % (repo,branch)
    github_prefix = 'https://github.com/'
    repo_url = urljoin(github_prefix, snapshot_path)
    return repo_url

def unpack_snapshot(snapshot_file,target_dir):
    import shutil
    shutil.unpack_archive(snapshot_file,target_dir)

def download_repo(repo, target_dir):
    import requests
    import pathlib

    url = repo_url(repo)

    downloaded_file = pathlib.Path(target_dir) / ("%s.zip" % repo)
    downloaded_file.write_bytes(requests.get(url).content)

