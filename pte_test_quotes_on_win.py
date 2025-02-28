import subprocess
from subprocess import run

proc = run(['mamba', "install", "--dry-run", 'setuptools<=73'],
           text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True, shell=False) # we do not need or want a shell for install
print(proc.stdout)
