/* jshint maxparams: 6 */
'use strict';

liveblog.require = {};
var merge = function(obj, source) {
    if (typeof source !== 'object') {
        return;
    }
    for (var key in source) {
        if (source.hasOwnProperty(key)) {
            if (typeof source[key] === 'object'){
                obj[key] = obj[key] ? obj[key] : {};
                merge(obj[key], source[key]);
            } else {
                obj[key] = source[key];
            }
        }
    }
};
var qs = window.location.href;
// if liveblog.dev parameter is there add additional properties.
if ((qs.indexOf('liveblog[dev]') !== -1) || liveblog.dev) {

    // search first into localstorage for liveblog.
    try {
        merge(liveblog, JSON.parse(localStorage.getItem('liveblog')));
    } catch (e){}

    // parse the current location href
    //     for the query parametes that starts with liveblog.
    //     override those properies over the existing global liveblog obj.
    //     parse only first and second level of the object.
    qs.replace(/liveblog\[([^?=&\]]+)\](\[([^?=&\]]+)\])?(=([^&]*))?/g, function (match, key, hasSub, subkey, hasEquality, value) {
        value = decodeURIComponent(value);
        if (hasSub) {
            liveblog[key] = liveblog[key] ? liveblog[key] : {};
            liveblog[key][subkey] = hasEquality ? value : true;
        } else {
            liveblog[key] = hasEquality ? value : true;
        }
    });
}
// @TODO: remove this defaults paths when backbone implementation will replace old one.
// if no path for scripts was define use the default path from ally-py implemenation server.
if (!liveblog.paths.scripts) {
    liveblog.paths.scripts = '/content/lib/livedesk-embed/scripts/js/';
}
// if no path for css was define use the default path from ally-py implemenation server.
if (!liveblog.paths.css) {
    liveblog.paths.css = '/content/lib/livedesk-embed/';
}
// @ENDTODO

// regex to catch all relevant parts of an url.
//   parameter[1] = protocol if there is one.
//   parameter[2] = hostname.
//   parameter[3] = port if there is one.
var urlRegex = /^(http[s]?:)?\/{2}([0-9.\-A-Za-z]+)(?::(\d+))?/,
    // regex to catch if the urlString has a http(s) or a relative protocol.
    protocolRegex = /^(http[s]?:)?\/{2}/;

// fix a urlString, forceing a relative protocol if the protocol http(s).
//   a url for browser always need a relative protocol see https bug @LB-1154
liveblog.browserUrl = function(urlString) {
    urlString = protocolRegex.test(urlString) ? urlString : '//' + urlString;
    urlString = urlString.replace(urlRegex, function(all, protocol, hostname, port) {
        return '//' +
                hostname +
                (port && (port !== '80' && port !== '443') ? ':' + port : '');
    });
    return urlString;
};
// fix servers frontend url
liveblog.servers.frontend = liveblog.browserUrl(liveblog.servers.frontend);
// fix the rest
liveblog.servers.rest = liveblog.browserUrl(liveblog.servers.rest);

// after aditional properties where added remake the baseUrl for loader and require.
liveblog.baseUrl = liveblog.require.baseUrl = liveblog.servers.frontend + liveblog.paths.scripts;

var loadMain = function() {
    if (liveblog.dev && !liveblog.emulateprod) {
        /*jshint unused:false*/
        // set the require object for development mode.
        var require = liveblog.require;
        liveblog.loadJs('node_modules/requirejs/require').setAttribute('data-main', liveblog.baseUrl + 'main');
    } else {
        // if is the production then object liveblog.require was already setup.
        liveblog.loadJs('build/main.min');
    }
};
// this is the callback after the version was loaded.
liveblog.callbackVersion = function(ver) {
    // add version to require urlArgs.
    liveblog.require.urlArgs = 'version=' + ver.major + '.' + ver.minor + '.' + ver.revision;
    if (liveblog.delay) {
        setTimeout(loadMain, parseInt(liveblog.delay, 10) * 1000);
    } else {
        loadMain();
    }
};

liveblog.loadJs('version');
