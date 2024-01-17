@echo off
setlocal

rem
if not defined PYMEENV ( set PYMEENV="pyme-shared" )
if not defined CONDAPATH ( set CONDAPATH="c:\ProgramData\Miniconda3\condabin" )
set PATH=%CONDAPATH%;%PATH%

call conda.bat activate %PYMEENV%

PYMEClusterofone

call conda deactivate

cmd /k
