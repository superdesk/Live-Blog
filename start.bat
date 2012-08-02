@ECHO OFF
setlocal
set PYTHONPATH=superdesk/plugins/livedesk;plugins/gui-core;plugins/test-dev;plugins/gui-action;components/ally-authentication-http/;
python.exe superdesk/distribution/application.py