@ECHO OFF
setlocal

set ALLYPY=..\ally-py
set PYTHONPATH=distribution/tools/distribute-0.6.27-py3.2.egg;

del %ALLYPY%\distribution\components\*.egg
python.exe %ALLYPY%\components\build_egg.py

del %ALLYPY%\distribution\plugins\*.egg
python.exe %ALLYPY%\plugins\build_egg.py

del distribution\components\*.egg
del distribution\plugins\*.egg
copy %ALLYPY%\distribution\plugins\*.egg distribution\plugins\
copy %ALLYPY%\distribution\components\*.egg distribution\components\

python.exe plugins\build_egg.py
