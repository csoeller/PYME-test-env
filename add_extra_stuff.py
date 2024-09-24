import condacmds as cmds
from condacmds import PymeBuild
#from condacmds import download_pyme_extra, download_pyme, build_pyme_extra, build_pyme, pyme_extra_install_plugins
from pathlib import Path

# this will become a replacement for mk_extra_stuff and will be based on reading the build settings
# from a previous pyme env build run

settings = cmds.read_env_settings('test-pyme-3.11-conda_4')
yaml_data = cmds.envfile('test-pyme-3.11-conda_4').read_text()
pb = PymeBuild.from_yaml(yaml_data)
print(pb)
