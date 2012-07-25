@ECHO OFF
setlocal
<<<<<<< HEAD
set PYTHONPATH=superdesk/plugins/livedesk;plugins/gui-core;plugins/test-dev;plugins/gui-action;
=======
set PYTHONPATH=superdesk/plugins/livedesk;plugins/gui-core;plugins/test-dev;plugins/gui-action;components/ally-authentication-http/;
>>>>>>> 5bb15fa123f7dd0f029ef9c16c6a811ca3430d35
python.exe superdesk/distribution/application.py