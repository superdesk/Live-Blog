'use strict';

define(['dust/core', 'lib/utils'], function(dust, utils) {

    var bypassExtensions = ['.ico'];
    dust.filters.amp = function(string) {
        if (utils.isServer) {

            string = string.replace(/<img([^>]*)>/g, function(all, attr) {
                var bypass = false;
                attr = attr.replace(/src\w*=\w*("|')([^\"\']+)("|')/g, function(at, qt, src) {
                    var chunks = [],
                        size = {height: -1, width: -1},
                        found = false;

                    for (var i = 0, count = bypassExtensions.length; i < count; i++) {
                        if (src.substr(src.length - 4) === bypassExtensions[i]) {
                            bypass = true;
                        }
                    }
                    if (bypass) {
                        return at;
                    }
                    try {
                        if (src.substr(0, 4).toLowerCase() !== 'http') {
                            src = 'http:' + src;
                        }

                        var imageSize = require('image-size'),
                            request = require('request');

                        var r = request.get({uri: src})
                            .on('data', function (chunk) {
                                chunks.push(chunk);
                                if (chunks.length > 2) {
                                    r.abort();
                                }
                            }).on('end', function() {
                                var buffer = Buffer.concat(chunks);
                                size = imageSize(buffer);
                                found = true;
                            });
                        setTimeout(function() { found = true; }, 150);
                        while (!found) {
                            require('deasync').runLoopOnce();
                        }
                    } catch (err) {
                        if (GLOBAL && GLOBAL.liveblogLogger) {
                            liveblogLogger.info('ERROR amp request: %s', err);
                        }
                    }
                    return 'src="' + src + '" height="' + size.height + '" width="' + size.width + '"';
                });
                if (bypass) {
                    return all;
                }
                return '<amp-img layout="responsive"' + attr + '/>';
            });

            return string;
        }
        return string;
    };
    return dust;
});
