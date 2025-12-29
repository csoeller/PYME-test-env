import json
import subprocess
from subprocess import run
import re
import sys
import logging
from pathlib import Path
import yaml
from warnings import warn

####################################
# conda/mamba/pip handling code
####################################

condacmd = "conda"
logger = logging.getLogger(__name__)

# NOTE: double check if we really need 
def shell_if_win32():
    if sys.platform == "win32":
        return dict(shell=True)
    else:
        return {}

SETTINGSDIR = Path('.environments')

def check_or_make_settingsdir():
    SETTINGSDIR.mkdir(exist_ok=True)

def envfile(env):
    return SETTINGSDIR / ("%s.yaml" % (env))
    
def check_env_registered(env):
    check_or_make_settingsdir()
    return envfile(env).is_file()

def read_env_settings(env):
    # check_or_make_settingsdir()
    with open(envfile(env)) as stream:
        settings = yaml.safe_load(stream)
        return settings
    
def write_env_settings_yaml(env,data):
    check_or_make_settingsdir()
    with envfile(env).open("w") as f:
       f.write(data)

# general approach taken: we run conda or pip commands in subprocesses
# there is a decent discussion in this stackoverflow question
# https://stackoverflow.com/questions/41767340/using-conda-install-within-a-python-script
# the answer by ws_e_c421 makes a good case which we adopt here
# the answer also references the pip docs https://pip.pypa.io/en/stable/user_guide/#using-pip-from-your-program
# which make exactly this point
# while conda seems not to have a dedicated manual discussion of this issue the points and examples
# given in ws_e_c421's answer make a good case to treat conda (or mamba) just like pip in this regard

def proc_error_msg(e):
    print("SUBPROCESS_ERR> Subprocess returned non-zero return code %d" % e.returncode)
    print("SUBPROCESS_ERR> Error during running cmd:\n\t\"%s\"" % e.cmd)
    if e.stdout is not None:
        print("SUBPROCESS_ERR> Subprocess output:\n", e.stdout)
    if e.stderr is not None:
        print("SUBPROCESS_ERR> Subprocess error messages:\n", e.stderr)
    print("SUBPROCESS_ERR> Terminating processing, check above for command that caused this error...")
    sys.exit(1)

def set_condacmd(cmd):
    global condacmd
    condacmd = cmd 

def conda_list(environment):
    global condacmd
    proc = run([condacmd, "list", "--json", "--name", environment],
               text=True, capture_output=True)
    return json.loads(proc.stdout)

def conda_envs(condacmd='conda'):
    proc = run([condacmd, "env", "list"], # note that we by default use conda, mamba has leading whitespace but now regex is fixed...
               text=True, capture_output=True, **shell_if_win32())
    lines = proc.stdout.split("\n")
    entry = re.compile("\s*(\S+)\s+[*]*\s*(\S+)")
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
    proc = run(cmd, text=True, capture_output=True,**shell_if_win32())
    return proc.stdout

def conda_remove(environment):
    global condacmd
    proc = run([condacmd, "remove", "-n", environment, "-y", "--all"], text=True, capture_output=True,**shell_if_win32())
    return proc.stdout

# use channels as needed
def conda_install(environment, packages, channels = None):
    global condacmd
    channelspecs = []
    for chan in channels:
        channelspecs += ["--channel", chan]
    cmd = [condacmd, "install", "--yes", "--name", environment] + channelspecs + list(packages)
    logger.info("command arg list is '%s'" % cmd)
    logger.info("\tcommand expanded '%s'" % ' '.join(cmd))
    
    try:
        proc = run(cmd, text=True, capture_output=True, check=True)
    except subprocess.CalledProcessError as e:
        proc_error_msg(e)
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

def check_yaml_installed():
    try:
        import yaml
    except ImportError:
        raise RuntimeError("we need pyyaml for saving/loading config info, please install using 'conda install -n base pyyaml'")

def pip_install(environment, packages):
    args = ['python', '-m', 'pip', 'install'] + list(packages)
    try:
        ret = run_cmd_in_environment(' '.join(args),environment,check=True)
    except subprocess.CalledProcessError as e:
        proc_error_msg(e)
    return ret


#################################################################
# PymeBuild class to collect some info and setup code for a build
#################################################################

import pathlib
import logging

def repobasename(repo):
    return repo.split('/')[-1]

class SourceInfo(object):
    def __init__(self,environment,build_dir,repo_name,from_git=False,branch='master',release=None,
                 install_test_file=None,post_install_cmd=None):
        self.target_environment = environment
        self.build_dir = build_dir
        self.repo_name = repo_name
        self.repo_branch = branch
        self.from_git = from_git
        self.release = release
        self.post_install_cmd = post_install_cmd
        self.install_test_file = install_test_file
        
        self._code_downloaded = False
        self._downloaded_file = None
        self._pck_dir = None

        if self.release is not None:
            self.download_mode = 'release'
        elif self.from_git:
            self.download_mode = 'git'
        else:
            self.download_mode = 'snapshot'

    def new_install_type(self):
        if self.install_test_file is None:
            return False
        if not self._code_downloaded:
            raise RuntimeError("trying to determine install type before code was downloaded")
        test_file_full_path = self.package_dir_name() / self.install_test_file
        return test_file_full_path.exists()

    def _install_cmd(self):
        if self.new_install_type():
            return "python -m pip install --no-deps --no-build-isolation --editable ."
        else:
            return "python setup.py develop"

    def _post_install_cmd(self):
        if self.post_install_cmd is None:
            return None # do nothing
        if self.new_install_type():
            cmd = self.post_install_cmd['new']
        else:
            cmd = self.post_install_cmd['old']

        return cmd
    
    def package_dir_name(self):
        # make and return package dir name from info in the object
        if self._pck_dir is not None: # caching
            return self._pck_dir
        
        if self.download_mode == 'snapshot' or self.download_mode == 'git':
            pck_dir = pathlib.Path(self.build_dir) / (repobasename(self.repo_name) + '-%s' % self.repo_branch)
        else: # should be release mode
            if not self._code_downloaded:
                raise RuntimeError("trying to determine release package dirname before code was downloaded")
            zip_path = self._downloaded_file
            if not zip_path.exists():
                raise RuntimeError("no zip file at zip path %s" % zip_path)
            import zipfile
            # zip file handler  
            zip = zipfile.ZipFile(zip_path)
            # list available files in the container
            repodir = zip.namelist()[0]
            zip.close()
            pck_dir = pathlib.Path(self.build_dir) / repodir
        self._pck_dir = pck_dir
        return pck_dir
    
    def download_url(self):
        # make and return download url from info in the object
        from urllib.parse import urljoin
        if self.download_mode == 'snapshot':
            snapshot_path = '%s/archive/refs/heads/%s.zip' % (self.repo_name,self.repo_branch)
            github_prefix = 'https://github.com/'
            repo_url = urljoin(github_prefix, snapshot_path)
            return repo_url
        elif self.download_mode == 'release':
            import requests
            import pathlib

            def get_release_url(repository,release_tag):
                release_url = "https://api.github.com/repos/{}/releases/tags/{}".format(repository,release_tag)
                return release_url

            def get_github_response(repository,release_tag):
                import requests
                release_url = get_release_url(repository,release_tag)
                release_response = requests.get(release_url)
                if release_response.ok:
                    return release_response
                else:
                    if release_response.reason == 'Not Found':
                        warn("release %s not found" % release_tag)
                    else:
                        warn("requesting release %s not successful, reason: %s" %(release_tag,release_response.reason))
                    return None

            response = get_github_response(self.repo_name, self.release)
            if response is None:
                raise RuntimeError("could not retrive release with of %s with release tag %s; is tag correct?" %
                                   (self.repo_name, self.release))
            zipurl = response.json().get('zipball_url')
            if zipurl is None:
                raise RuntimeError("could not retrieve zip url for release %s" % release)
            return zipurl
        else:
            return None # this should be git mode

    def download(self):
        if self.download_mode == 'snapshot' or self.download_mode == 'release':
            import requests
            url = self.download_url()
            downloaded_file = pathlib.Path(self.build_dir) / ("%s.zip" % repobasename(self.repo_name))
            downloaded_file.write_bytes(requests.get(url).content)
            self._downloaded_file = downloaded_file
            import shutil
            shutil.unpack_archive(downloaded_file,self.build_dir)
        else:
            # git based download
            def mk_git_url(repo):
                from urllib.parse import urljoin
                return urljoin('https://github.com/', "%s.git" % repo)

            import git

            repo = git.Repo.clone_from(mk_git_url(self.repo_name),
                                       self.package_dir_name(),
                                       branch=self.repo_branch)

        self._code_downloaded = True
        
    def build_and_install(self):
        ret = run_cmd_in_environment(self._install_cmd(), self.target_environment, cwd=self.package_dir_name())
        logging.info("building %s..." % repobasename(self.repo_name))
        logging.info(ret)

    def postinstall(self):
        cmd = self._post_install_cmd()
        if cmd is None:
            return
        ret = run_cmd_in_environment(cmd, self.target_environment, cwd=self.package_dir_name())
        logging.info("running postinstall command for %s..." % repobasename(self.repo_name))
        logging.info(ret)
 

class PymeBuild(object):
    def __init__(self,pythonver,build_dir='build-test',condacmd='conda',
                 environment=None, mk_build_dir=True, start_log=True,
                 with_pyme_depends=True,with_pyme_build=True,with_pymex=True,
                 with_recipes=False,
                 pyme_repo=None, pyme_branch=None,
                 pymex_repo=None, pymex_branch=None,
                 use_git=False, suffix=None,
                 strict_conda_forge_channel=True, dry_run=False,
                 xtra_packages=None, logfile=None,
                 pyme_release=None,pymex_release=None,
                 ):
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
        self.with_pyme_build = with_pyme_build
        self.with_pymex = with_pymex
        self.with_recipes = with_recipes
                
        self.pyme_repo=pyme_repo
        self.pyme_branch=pyme_branch
        self.pyme_release=pyme_release
        self.pymex_repo=pymex_repo
        self.pymex_branch=pymex_branch
        self.pymex_release=pymex_release

        self.use_git = use_git

        self.strict_conda_forge_channel = strict_conda_forge_channel
        self.dry_run = dry_run
        self.xtra_packages = xtra_packages
        
        if mk_build_dir and not dry_run:
            self.build_dir.mkdir(exist_ok=True)            

        self.logging = start_log
        self.setup_logging(logfile)

        self.register_environment()

        self.pyme_src = SourceInfo(self.env,build_dir=self.build_dir,repo_name=self.pyme_repo,
                                   from_git=self.use_git,branch=self.pyme_branch,release=self.pyme_release,
                                   install_test_file='meson.build',post_install_cmd=None)
        self.pymex_src = SourceInfo(self.env,build_dir=self.build_dir,repo_name=self.pymex_repo,
                                    from_git=self.use_git,branch=self.pymex_branch,release=self.pymex_release,
                                    install_test_file='pyproject.toml',
                                    post_install_cmd={
                                        'new' : 'pymex_install_plugins',
                                        'old' : 'python install_plugins.py',
                                    }) # arguments derived from pbld
    
    def check_consistency(self):
        if self.pyme_release is not None and self.use_git:
            raise RuntimeError("you cannot choose to install a release AND use git mode; please choose either")
        if self.pymex_release is not None and self.use_git:
            raise RuntimeError("you cannot choose to install a release AND use git mode; please choose either")

    def setup_logging(self,logfile=None):
        if self.logging:
            if logfile is None:
                self.logfile = self.build_dir / ('build-%s.log' % self.env)
            else:
                self.logfile = self.build_dir / logfile.replace('$environment$',self.env) # this should be using the buildstem somehow
        else:
            self.logfile = None

        if self.logging and not self.dry_run:
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

    # here we want to add saving the config as yaml, check if config already exists, etc
    def register_environment(self):
        if check_env_registered(self.env):
            self._settings = read_env_settings(self.env)
        else:
            write_env_settings_yaml(self.env,self.to_yaml())

    def to_yaml(self):
        import yaml
        settings = {}
        attr_names=[a for a in dir(self) if not a.startswith('_') and not callable(getattr(self, a))]
        for a in attr_names:
            attr = getattr(self,a)
            if isinstance(attr,Path):
                settings[a] = attr.as_posix()
            else:
                settings[a] = attr
        return yaml.dump(settings)

    @classmethod
    def from_yaml(cls,data):
        obj = cls.__new__(cls)  # Does not call __init__
        settings = yaml.safe_load(data)
        super(PymeBuild, obj).__init__()
        for a in settings:
            if a == 'build_dir':
                setattr(obj,a,Path(settings[a]))
            else:
                setattr(obj,a,settings[a])
        obj._settings = settings
        return obj
    
    def __str__(self):
        from textwrap import dedent
        return dedent(f"""
        PYME test build: python={self.pythonver}, environment={self.env},
        build_dir={self.build_dir}, condacmd={self.condacmd},
        with_pyme_depends={self.with_pyme_depends}, with_pymex={self.with_pymex},
        pyme_repo={self.pyme_repo}, pyme_branch={self.pyme_branch},
        pymex_repo={self.pymex_repo}, pymex_branch={self.pymex_branch},
        pyme_release={self.pyme_release},pymex_release={self.pymex_release},
        with_recipes={self.with_recipes}, logging={self.logging}, logfile={self.logfile},
        use_git={self.use_git}, suffix={self.suffix},
        strict_conda_forge_channel={self.strict_conda_forge_channel}, dry_run={self.dry_run},
        xtra_packages={self.xtra_packages}
        """)
