(function(){

    var fs, getXhr,
        progIds = ['Msxml2.XMLHTTP', 'Microsoft.XMLHTTP', 'Msxml2.XMLHTTP.4.0'],
        fetchText = function () {
            throw new Error('Environment unsupported.');
        },
        buildMap = [],
        isBrowser = (typeof window !== "undefined" && window.navigator && window.document) || typeof importScripts !== "undefined",
        isNode = typeof process !== "undefined" && process.versions && !!process.versions.node,
		pathPrefix = '';
        dustCompilerLibrary = ['dust/compiler','dust/i18n_parse'];
		dustCoreLibrary = 'dust/core';

    if (isBrowser) {
        // Browser action
        getXhr = function () {
            //Would love to dump the ActiveX crap in here. Need IE 6 to die first.
            var xhr, i, progId;
            if (typeof XMLHttpRequest !== "undefined") {
                return new XMLHttpRequest();
            } else {
                for (i = 0; i < 3; i++) {
                    progId = progIds[i];
                    try {
                        xhr = new ActiveXObject(progId);
                    } catch (e) {}

                    if (xhr) {
                        progIds = [progId];  // so faster next time
                        break;
                    }
                }
            }

            if (!xhr) {
                throw new Error("getXhr(): XMLHttpRequest not available");
            }

            return xhr;
        };

        fetchText = function (url, callback) {
            var xhr = getXhr();
            xhr.open('GET', url, true);
            xhr.onreadystatechange = function (evt) {
                //Do not explicitly handle errors, those should be
                //visible via console output in the browser.
                if (xhr.readyState === 4) {
                    callback(xhr.responseText);
                }
            };
            xhr.send(null);
        };

    } else if (isNode) {
        //Using special require.nodeRequire, something added by r.js.
        fs = require.nodeRequire('fs');
        fetchText = function (path, callback) {
            callback(fs.readFileSync(path, 'utf8'));
        };
    }

    define({
        version: '0.0.1',

        write: function (pluginName, name, write) {
            if (name in buildMap) {
                var text = buildMap[name];
                write.asModule(pluginName + "!" + name, text);
                write("define('" + pluginName + "!" + name  + "', function () { return null;});\n");
            }
        },

        load: function (name, parentRequire, load, config) {
			var self = this;
            if (isBrowser) {
                require(dustCompilerLibrary, function(dust, i18n_parse){
					self.process(dust, name, parentRequire, load, config, i18n_parse);
                });
            } else if (isNode) {
                self.process(require.nodeRequire('dust'), name, parentRequire, load, config);
            }
        },

        process: function(dust, name, parentRequire, load, config, i18n_parse) {
			var prefix = '',prefixTemplate=''
			if( name.indexOf('>') === -1 ) {
				prefix = config.templatePaths.default;
			} else {
				var arr = name.split('>');
				prefixTemplate = arr[0] + '>';
				prefix = config.templatePaths.plugin.replace('{plugin}',arr[0]);
				name = arr[1];				
			}
			var self = this,
                path = parentRequire.toUrl( prefix + name + '.dust');
            fetchText(path, function(data){
				data = i18n_parse(data);
				var text = "define('tmpl!" + prefixTemplate + name + "', ['"+dustCoreLibrary+"'], function (dust) {"
						+ dust.compile(data, prefixTemplate + name) + "\n"
						+ "return { render: function(context, callback) {dust.render('" + prefixTemplate + name + "', context, callback); }}"
						+ "});\n"
                if (config.isBuild) {
                    buildMap[name] = text;
                }

                if (!config.isBuild) {
                    text += "\r\n//@ sourceURL=" + path;
                }
                load.fromText(prefixTemplate + name, isNode ? '' : text);			
                parentRequire([prefixTemplate + name], function (value) {
                    load(value);
                });
            });
        }
    });

}());