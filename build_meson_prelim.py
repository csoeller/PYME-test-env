import condacmds as cmds
import platform
import subprocess

cmds.check_condaenv('base') # check we are running in the base environment

def build_pyme_meson(environment,repodir):
    arch = platform.uname().machine
    build_cmd = 'python -m pip install --no-deps --no-build-isolation --editable .' # largely an equivalent of python setup.py develop
    if platform.system() != 'Windows':
        archcmd = 'export ARCHFLAGS="-arch %s"' % arch
        combined_cmd = "%s ; %s" % (archcmd,build_cmd)
    else:
        combined_cmd = build_cmd
    result = cmds.run_cmd_in_environment(combined_cmd, environment, cwd=repodir)
    return result

environment = 'test-pyme-3.11-conda_ms2'
repodir = 'build-test-py3.11-conda_ms2/python-microscopy-master'

print("installing packages for build process...")
result = cmds.conda_install(environment, 'python-build meson meson-python'.split(), channels = ['conda-forge'])
print(result)

print("building pyme with meson...")
result = build_pyme_meson(environment,repodir)
print(result)

print("testing install...")
result = cmds.run_cmd_in_environment('python -c "import PYME.version; print(PYME.version.version)"',environment,check=True)
print("Got PYME version %s" % result)
