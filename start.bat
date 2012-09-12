@ECHO OFF
setlocal
set PYTHONPATH=superdesk/plugins/livedesk;plugins/gui-core;plugins/test-dev
del superdesk\distribution\workspace\superdesk.db
python.exe superdesk/distribution/application.py