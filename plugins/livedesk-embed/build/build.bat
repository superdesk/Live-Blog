@echo off
@echo on
REM java -classpath js.jar;compiler.jar -Xss128m org.mozilla.javascript.tools.shell.Main r.js -o core.js
REM java -classpath js.jar;compiler.jar -Xss128m org.mozilla.javascript.tools.shell.Main r.js -o default.js
REM java -classpath js.jar;compiler.jar -Xss128m org.mozilla.javascript.tools.shell.Main r.js -o zeit_solo-desktop.js
REM java -classpath js.jar;compiler.jar -Xss128m org.mozilla.javascript.tools.shell.Main r.js -o zeit-desktop.js
REM java -classpath js.jar;compiler.jar -Xss128m org.mozilla.javascript.tools.shell.Main r.js -o rp-desktop.js
REM java -classpath js.jar;compiler.jar -Xss128m org.mozilla.javascript.tools.shell.Main r.js -o nzz-desktop.js
java -classpath js.jar;compiler.jar -Xss128m org.mozilla.javascript.tools.shell.Main r.js -o rhrnt.js
java -classpath js.jar;compiler.jar -Xss128m org.mozilla.javascript.tools.shell.Main r.js -o rhrnt-section.js

REM java -classpath js.jar;compiler.jar -Xss128m org.mozilla.javascript.tools.shell.Main r.js -o tageswoche-solo-desktop.js
REM java -classpath js.jar;compiler.jar -Xss128m org.mozilla.javascript.tools.shell.Main r.js -o tageswoche-multi-desktop.js
REM java -classpath js.jar;compiler.jar -Xss128m org.mozilla.javascript.tools.shell.Main r.js -o main.js