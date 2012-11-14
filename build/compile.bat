REM java -jar compiler.jar --js hello.js --js_output_file hello-compiled.js
@ECHO OFF
setlocal
SET FULLPATH=
SET LIVEPATH=%FULLPATH%..\superdesk\plugins\livedesk\
SET EMBEDPATH=%LIVEPATH%gui-resources\scripts\js\embed\
java -jar compiler.jar --js %EMBEDPATH%gizmo.dev.js --js_output_file %EMBEDPATH%gizmo.js
java -jar compiler.jar --js %EMBEDPATH%livedesk-embed.dev.js --js_output_file %EMBEDPATH%livedesk-embed.js
