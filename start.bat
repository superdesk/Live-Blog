@ECHO OFF
setlocal
set ALLYPY=..
set PYTHONPATH=distribution\tools\distribute-0.6.27-py3.2.egg;

python.exe %ALLYPY%\components\build_egg.py

python.exe %ALLYPY%\plugins\build_egg.py

xcopy %ALLYPY%\distribution\plugins\*.egg distribution\plugins\ /D/Y>NUL
xcopy %ALLYPY%\distribution\components\*.egg distribution\components\ /D/Y>NUL

python.exe plugins\build_egg.py

IF NOT EXIST distribution\application.properties python distribution\application.py -dump

python.exe distribution\application.py
