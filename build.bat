@ECHO OFF
setlocal
set PYTHONPATH=distribution/libraries/distribute-0.6.27-py3.2.egg;
python.exe components\build_egg.py
python.exe superdesk\plugins\build_egg.py
python.exe plugins\build_egg.py