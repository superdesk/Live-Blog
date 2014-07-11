@echo off
@echo on
java -classpath js.jar;compiler.jar -Xss100m org.mozilla.javascript.tools.shell.Main r.js -o core.js
java -classpath js.jar;compiler.jar -Xss100m org.mozilla.javascript.tools.shell.Main r.js -o default.js
java -classpath js.jar;compiler.jar -Xss100m org.mozilla.javascript.tools.shell.Main r.js -o zeit_solo-desktop.js
java -classpath js.jar;compiler.jar -Xss100m org.mozilla.javascript.tools.shell.Main r.js -o zeit-desktop.js
java -classpath js.jar;compiler.jar -Xss100m org.mozilla.javascript.tools.shell.Main r.js -o rp-desktop.js
java -classpath js.jar;compiler.jar -Xss100m org.mozilla.javascript.tools.shell.Main r.js -o nzz-desktop.js
java -classpath js.jar;compiler.jar -Xss100m org.mozilla.javascript.tools.shell.Main r.js -o rhrnt.js
java -classpath js.jar;compiler.jar -Xss100m org.mozilla.javascript.tools.shell.Main r.js -o rhrnt-section.js
java -classpath js.jar;compiler.jar -Xss100m org.mozilla.javascript.tools.shell.Main r.js -o brasil247.js

java -classpath js.jar;compiler.jar -Xss100m org.mozilla.javascript.tools.shell.Main r.js -o tageswoche-solo-desktop.js
java -classpath js.jar;compiler.jar -Xss100m org.mozilla.javascript.tools.shell.Main r.js -o tageswoche-multi-desktop.js

java -classpath js.jar;compiler.jar -Xss100m org.mozilla.javascript.tools.shell.Main r.js -o sf-internal.js