@ECHO OFF
setlocal
set PYTHONPATH=distribution/tools/distribute-0.6.27-py3.2.egg;
del distribution\components\*.egg
python.exe components\build_egg.py
del distribution\plugins\*.egg
python.exe plugins\build_egg.py
del superdesk\distribution\components\*.egg
del superdesk\distribution\plugins\*.egg
copy distribution\plugins\*.egg superdesk\distribution\plugins\
copy distribution\components\*.egg superdesk\distribution\components\
python.exe superdesk\plugins\build_egg.py
