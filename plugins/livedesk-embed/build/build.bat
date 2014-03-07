@echo off
@echo on
java -classpath js.jar;compiler.jar -Xss128m org.mozilla.javascript.tools.shell.Main r.js -o core.js
REM java -classpath js.jar;compiler.jar -Xss128m org.mozilla.javascript.tools.shell.Main r.js -o default.js
REM java -classpath js.jar;compiler.jar -Xss128m org.mozilla.javascript.tools.shell.Main r.js -o zeit_solo-desktop.js
REM java -classpath js.jar;compiler.jar -Xss128m org.mozilla.javascript.tools.shell.Main r.js -o zeit-desktop.js
java -classpath js.jar;compiler.jar -Xss128m org.mozilla.javascript.tools.shell.Main r.js -o rp-desktop.js

java -classpath js.jar;compiler.jar -Xss128m org.mozilla.javascript.tools.shell.Main r.js -o tageswoche-solo-desktop.js
java -classpath js.jar;compiler.jar -Xss128m org.mozilla.javascript.tools.shell.Main r.js -o tageswoche-multi-desktop.js
REM java -classpath js.jar;compiler.jar -Xss128m org.mozilla.javascript.tools.shell.Main r.js -o main.js
