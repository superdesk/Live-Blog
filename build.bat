@ECHO OFF
setlocal
set PYTHONPATH=distribution/libraries/distribute-0.6.27-py3.2.egg;
cd components	
python.exe build-egg.py