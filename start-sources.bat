@ECHO OFF
setlocal
SET FULLPATH=
SET ALLYCOM=%FULLPATH%components\
set PYTHONPATH=%ALLYCOM%ally-api
set PYTHONPATH=%PYTHONPATH%;%ALLYCOM%ally-authentication
set PYTHONPATH=%PYTHONPATH%;%ALLYCOM%ally-authentication-core
set PYTHONPATH=%PYTHONPATH%;%ALLYCOM%ally-authentication-http
set PYTHONPATH=%PYTHONPATH%;%ALLYCOM%ally-core
set PYTHONPATH=%PYTHONPATH%;%ALLYCOM%ally-core-http
set PYTHONPATH=%PYTHONPATH%;%ALLYCOM%ally-core-plugin
set PYTHONPATH=%PYTHONPATH%;%ALLYCOM%ally-core-sqlalchemy
set PYTHONPATH=%PYTHONPATH%;%ALLYCOM%ally-utilities
set PYTHONPATH=%PYTHONPATH%;%ALLYCOM%support-administration
set PYTHONPATH=%PYTHONPATH%;%ALLYCOM%support-cdm
set PYTHONPATH=%PYTHONPATH%;%ALLYCOM%support-development

SET ALLYPLUG=%FULLPATH%plugins\
set PYTHONPATH=%PYTHONPATH%;%ALLYPLUG%gui-action
set PYTHONPATH=%PYTHONPATH%;%ALLYPLUG%gui-core
set PYTHONPATH=%PYTHONPATH%;%ALLYPLUG%internationalization
set PYTHONPATH=%PYTHONPATH%;%ALLYPLUG%introspection-request
set PYTHONPATH=%PYTHONPATH%;%ALLYPLUG%support-sqlalchemy

SET SUPERPLUG=%FULLPATH%superdesk\plugins\
REM set PYTHONPATH=%PYTHONPATH%;%SUPERPLUG%ffmpeg-binary
set PYTHONPATH=%PYTHONPATH%;%SUPERPLUG%livedesk
set PYTHONPATH=%PYTHONPATH%;%SUPERPLUG%media-archive
set PYTHONPATH=%PYTHONPATH%;%SUPERPLUG%media-archive-audio
set PYTHONPATH=%PYTHONPATH%;%SUPERPLUG%media-archive-image
set PYTHONPATH=%PYTHONPATH%;%SUPERPLUG%media-archive-video
set PYTHONPATH=%PYTHONPATH%;%SUPERPLUG%superdesk
set PYTHONPATH=%PYTHONPATH%;%SUPERPLUG%superdesk-address
set PYTHONPATH=%PYTHONPATH%;%SUPERPLUG%superdesk-article
set PYTHONPATH=%PYTHONPATH%;%SUPERPLUG%superdesk-authentication
set PYTHONPATH=%PYTHONPATH%;%SUPERPLUG%superdesk-collaborator
set PYTHONPATH=%PYTHONPATH%;%SUPERPLUG%superdesk-country
set PYTHONPATH=%PYTHONPATH%;%SUPERPLUG%superdesk-language
set PYTHONPATH=%PYTHONPATH%;%SUPERPLUG%superdesk-person
set PYTHONPATH=%PYTHONPATH%;%SUPERPLUG%superdesk-post
set PYTHONPATH=%PYTHONPATH%;%SUPERPLUG%superdesk-source
set PYTHONPATH=%PYTHONPATH%;%SUPERPLUG%superdesk-user

del superdesk\distribution\workspace\superdesk.db
python superdesk\distribution\application.py