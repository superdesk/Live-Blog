@ECHO OFF
setlocal
set PYTHONPATH=superdesk/plugins/livedesk;plugins/gui-core;plugins/test-dev;superdesk/plugins/superdesk-article;
del superdesk\distribution\workspace\superdesk.db
python.exe superdesk/distribution/application.py