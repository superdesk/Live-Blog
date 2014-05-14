/**
 * AMD implementation for dust.js
 * This is based on require-cs code.
 * see: http://github.com/jrburke/require-cs for details
 */

/* jshint expr: true */
/* global define, window, process, require */
'use strict';

define(['dust', 'lib/require/i18n-parse'], function(dust, i18nParse) {
    var fetchText = function () {
            throw new Error('Environment unsupported.');
        },
        buildMap = {};
    dust || (dust = exports);

    if (typeof process !== 'undefined' &&
               process.versions &&
               !!process.versions.node) {
        //Using special require.nodeRequire, something added by r.js.
        var fs = require.nodeRequire('fs');
        fetchText = function (path, callback) {
            callback(fs.readFileSync(path, 'utf8'));
        };
    } else if ((typeof window !== 'undefined' && window.navigator && window.document) || typeof importScripts !== 'undefined') {
        fetchText = function (url, callback) {
            /*!
             * If dataType is requested as text then it fails due to some cdm issues with ie
             * so request it as json and in error method if is a json parsing issue we are good to go.
             */
            require(['lib/jquery/xdomainrequest'], function($) {
                $.ajax({
                    //dataType: 'json',
                    url: url,
                    error: function(xhr, textStatus, errorThrown) {
                        if (textStatus === 'parsererror'){
                            callback(xhr.responseText);
                        }
                    },
                    //contentType: 'application/octet-stream',
                    success: function(data) {
                        callback(data);
                    }
                });
            });
        };
        // end browser.js adapters
    }

    return {
        pluginBuilder: 'lib/require/tmpl-builder',
        write: function (pluginName, name, write) {
            if (buildMap.hasOwnProperty(name)) {
                var text = buildMap[name];
                write.asModule(pluginName + '!' + name, text);
            }
        },

        load: function (name, parentRequire, load, config) {
            var path = parentRequire.toUrl(name + '.dust');
            fetchText(path, function (text) {
                text = i18nParse(text);
				//Do dust transform.
                try {
                    text = 'define(["dust"],function(dust){' + dust.compile(text, name) + ' return {render: function(context, callback) {return dust.render("' + name + '", context, callback)}}})';
                }
                catch (err) {
                    err.message = 'In ' + path + ', ' + err.message;
                    throw(err);
                }

                //Hold on to the transformed text if a build.
                if (config.isBuild) {
                    buildMap[name] = text;
                }

                //IE with conditional comments on cannot handle the
                //sourceURL trick, so skip it if enabled.
                /*@if (@_jscript) @else @*/
                // if (!config.isBuild) {
                //     text += '\r\n//@ sourceURL=' + path;
                // }
                /*@end@*/
                load.fromText('tmpl!' + name, text);
            });
        }
    };
});
