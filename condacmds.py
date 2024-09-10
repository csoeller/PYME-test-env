import json
import subprocess
from subprocess import run
import re
import sys
import logging
from pathlib import Path

####################################
# conda/mamba/pip handling code
####################################

condacmd = "conda"
logger = logging.getLogger(__name__)

# general approach taken: we run conda or pip commands in subprocesses
# there is a decent discussion in this stackoverflow question
# https://stackoverflow.com/questions/41767340/using-conda-install-within-a-python-script
# the answer by ws_e_c421 makes a good case which we adopt here
# the answer also references the pip docs https://pip.pypa.io/en/stable/user_guide/#using-pip-from-your-program
# which make exactly this point
# while conda seems not to have a dedicated manual discussion of this issue the points and examples
# given in ws_e_c421's answer make a good case to treat conda (or mamba) just like pip in this regard

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
    cmd = [condacmd, "create", "--quiet", "--json", "-y", "--name", environment] + channelspecs + packages
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

def mk_compound_cmd(*cmds):
    from sys import platform
    if platform == "linux" or platform == "linux2":
        sep = ' && '
    elif platform == "darwin":
        sep = ' && '
    elif platform == "win32":
        sep = ' && '

    return sep.join(cmds)

def condash_location():
    import shutil
    import pathlib
    condapth = pathlib.Path(shutil.which('conda'))
    parts = condapth.parts
    if 'condabin' in parts:
        initial_path = pathlib.Path().joinpath(*parts[0:parts.index('condabin')])
    elif 'bin' in parts:
        initial_path = pathlib.Path().joinpath(*parts[0:parts.index('bin')])
    else:
        logging.warn("condabin or bin not in path %s for conda" % condapth)
        raise RuntimeError('cannot find conda.sh')
    condash_path =  initial_path / 'etc/profile.d/conda.sh'
    if condash_path.exists():
        return condash_path
    else:
        logging.warn("condash at path %s does not exist" % condash_path)
    raise RuntimeError('cannot find conda.sh')

def run_cmd_in_environment(cmd, environment,**kwargs): # kwargs are passed to subprocess.run()
    global condacmd
    import platform
    if platform.system() in ['Linux','Darwin']: # should be general darwin or linux with unix type shells
        # for why we do this, see https://copyprogramming.com/howto/conda-activate-command-not-working-on-mac
        # to find conda.sh we try to find conda.sh starting from the path to conda, see condash_location() above
        cmds = ['source %s' % condash_location(),
                "%s activate %s" % ('conda', environment), # we hardcode conda for that, we seem to get 'mamba init' issues in unix shells otherwise
                cmd]
    else:
        cmds = ["%s activate %s" % ('conda', environment),
                cmd]
    compoundcmd = mk_compound_cmd(*cmds)
    logger.info("command is %s" % compoundcmd)
    # note the use of stdout=... and stderr=... captures STDERR for us; capture_output=True does not seem to do that
    proc = run(compoundcmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, **kwargs)
    return proc.stdout

def check_condaenv(target_env):
    import os
    env = os.getenv("CONDA_DEFAULT_ENV")
    if env is None:
        import warnings
        warnings.warn("Cannot determine conda environment, giving up...")
        warnings.warn("Check manually that you are running in the base environment")
        answer = input("Are you sure you want to continue?")
        if answer.lower() not in ["y","yes"]:
            print("aborting...")
            import sys
            sys.exit(0)
        return
    else:
        if env == target_env:
            logger.info("running in %s environment" % env)
            return
        else:
            raise RuntimeError("needs to run in base environment, however %s environment is activated, please check" % env)

def pip_install(environment, packages):
    args = ['python', '-m', 'pip', 'install'] + list(packages)
    return run_cmd_in_environment(' '.join(args),environment)

#################################
# github repository handling code
#################################


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
    
def download_repo_snapshot(repo, target_dir,branch='master'):
    import requests
    import pathlib

    url = repo_url(repo,branch=branch)

    downloaded_file = pathlib.Path(target_dir) / ("%s.zip" % repobasename(repo))
    downloaded_file.write_bytes(requests.get(url).content)

def repo_dirname(repo,branch='master'):
    return repobasename(repo) + '-%s' % branch

def repo_dir(repo,branch='master',build_dir="build-test"):
    import pathlib
    return pathlib.Path(build_dir) / repo_dirname(repo,branch=branch)

def repo_cmd(cmd,repo,environment,branch='master',build_dir="build-test"):
    # need to see if a relative path is enough
    repodir = repo_dir(repo,branch=branch,build_dir=build_dir)
    # we could make the install mode selectable
    result = run_cmd_in_environment(cmd, environment, cwd=repodir)
    return result

def build_repo(repo,environment,branch='master',build_dir="build-test"):    
    return repo_cmd("python setup.py develop",repo,environment,
                    branch=branch,build_dir=build_dir)

def repo_install_plugins(repo,environment,branch='master',build_dir="build-test"):
    return repo_cmd("python install_plugins.py",repo,environment,
                    branch=branch,build_dir=build_dir)

# used in 'git' mode to clone the full repository locally
def mk_git_url(repo):
    from urllib.parse import urljoin
    return urljoin('https://github.com/', "%s.git" % repo)

def clone_repo(repo,target_dir,branch='master'):
    import git

    repo = git.Repo.clone_from(mk_git_url(repo), # we need to define this function
                               target_dir,
                               branch=branch)

def download_repo_generic(repo,build_dir,branch,mode):
    if mode == 'snapshot':
        download_repo_snapshot(repo, build_dir,branch=branch)
        unpack_snapshot(Path(build_dir) / ("%s.zip" % repobasename(repo)), build_dir)
    elif mode =='git':
        target_dir = Path(build_dir) / repo_dirname(repo,branch=branch)
        clone_repo(repo,target_dir,branch=branch)
    else:
        raise RuntimeError("unknown mode '%s'" % mode)    

def build_repo_generic(environment,repo,build_dir,branch):
    ret = build_repo(repo,environment,build_dir=build_dir,branch=branch)
    logging.info("building %s..." % repobasename(repo))
    logging.info(ret)

def repo_install_plugins_generic(environment,build_dir,repo,branch):
    ret = repo_install_plugins(repo,environment,build_dir=build_dir,branch=branch)
    logging.info("installing %s plugins..." % repobasename(repo))
    logging.info(ret)
    
def download_pyme_extra(build_dir="build-test",branch='master',repo='csoeller/PYME-extra',mode='snapshot'):
    download_repo_generic(repo,build_dir,branch,mode)
    
def download_pyme(build_dir="build-test",branch='master',repo='python-microscopy/python-microscopy',mode='snapshot'):
    download_repo_generic(repo,build_dir,branch,mode)

def build_pyme(environment,build_dir="build-test",repo='python-microscopy/python-microscopy',branch='master'):
    build_repo_generic(environment,repo,build_dir,branch)

def build_pyme_extra(environment,build_dir="build-test",repo='csoeller/PYME-extra',branch='master'):
    build_repo_generic(environment,repo,build_dir,branch)

def pyme_extra_install_plugins(environment,build_dir="build-test",repo='csoeller/PYME-extra',branch='master'):
    repo_install_plugins_generic(environment,build_dir,repo,branch)


#################################################################
# PymeBuild class to collect some info and setup code for a build
#################################################################

import pathlib
import logging
class PymeBuild(object):
    def __init__(self,pythonver,build_dir='build-test',condacmd='conda',
                 environment=None, mk_build_dir=True, start_log=True,
                 with_pyme_depends=True,with_pymex=True,
                 with_recipes=False,
                 pyme_repo=None, pyme_branch=None,
                 pymex_repo=None, pymex_branch=None,
                 use_git=False, suffix=None,
                 strict_conda_forge_channel=True, dry_run=False,
                 xtra_packages=None, logfile=None):
        self.suffix = suffix
        self.pythonver = pythonver
        if self.suffix is None:
            pfix = ''
        else:
            pfix = self.suffix
        build_dir_name = build_dir + "-py%s-%s" % (pythonver,condacmd) + pfix
        self.build_dir = pathlib.Path(build_dir_name)
        self.condacmd = condacmd
        set_condacmd(self.condacmd)
        if environment is None:
            self.env = 'test-pyme-%s-%s' % (self.pythonver,self.condacmd)
            self.env = self.env + pfix
        else:
            self.env = environment
        self.with_pyme_depends = with_pyme_depends
        self.with_pymex = with_pymex
        self.with_recipes = with_recipes
        self.logging = start_log
        if self.logging:
            if logfile is None:
                self.logfile = self.build_dir / ('build-%s.log' % self.env)
            else:
                self.logfile = self.build_dir / logfile.replace('$environment$',self.env) # this should be using the buildstem somehow
        else:
            self.logfile = None
        
        self.pyme_repo=pyme_repo
        self.pyme_branch=pyme_branch
        self.pymex_repo=pymex_repo
        self.pymex_branch=pymex_branch

        self.use_git = use_git

        self.strict_conda_forge_channel = strict_conda_forge_channel
        self.dry_run = dry_run
        self.xtra_packages = xtra_packages
        
        if mk_build_dir and not dry_run:
            self.build_dir.mkdir(exist_ok=True)

        if start_log and not self.dry_run:
            # set up logging to file
            logging.basicConfig(
                filename=self.logfile,
                # encoding='utf-8', # earlier py 3.X has no encoding option yet
                level=logging.DEBUG
            )

            # set up logging to console
            console = logging.StreamHandler()
            console.setLevel(logging.DEBUG)
            # add the handler to the root logger
            logging.getLogger('').addHandler(console)

            logger.info('building PYME...')
            logger.info(self)

        if self.dry_run:
            logging.basicConfig( # assuming this goes to console without filename argument
                # encoding='utf-8', # earlier py 3.X has no encoding option yet
                level=logging.DEBUG
            )
            logger.info(self)
            
    def __str__(self):
        from textwrap import dedent
        return dedent(f"""
        PYME test build: python={self.pythonver}, environment={self.env},
        build_dir={self.build_dir}, condacmd={self.condacmd},
        with_pyme_depends={self.with_pyme_depends}, with_pymex={self.with_pymex},
        pyme_repo={self.pyme_repo}, pyme_branch={self.pyme_branch},
        pymex_repo={self.pymex_repo}, pymex_branch={self.pymex_branch},
        with_recipes={self.with_recipes}, logging={self.logging}, logfile={self.logfile},
        use_git={self.use_git}, suffix={self.suffix},
        strict_conda_forge_channel={self.strict_conda_forge_channel}, dry_run={self.dry_run},
        xtra_packages={self.xtra_packages}
        """)
