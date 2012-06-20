@ECHO OFF
setlocal
set PYTHONPATH=superdesk/plugins/livedesk;plugins/gui-core;plugins/test-dev
python.exe superdesk/distribution/application.py
