@ECHO OFF
setlocal
del superdesk\distribution\workspace\*.db
python.exe superdesk/distribution/application.py