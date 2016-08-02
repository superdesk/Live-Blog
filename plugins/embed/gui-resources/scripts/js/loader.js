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
// check if there is a query string with liveblog[dev] or liveblog.dev
//   and if so overide the one in global liveblog object.
var qsReg = 'liveblog[\\[\\.]dev[\\]]?(=([^&#]*))?';
qs.replace(new RegExp(qsReg, 'g'), function (match, hasEquality, value) {
    liveblog.dev = hasEquality ? (value.toLowerCase() === 'true' ? true : false) : true;
});

// if liveblog.dev parameter is there add additional properties.
if (liveblog.dev) {
    // search first into localstorage for liveblog.
    try {
        merge(liveblog, JSON.parse(localStorage.getItem('liveblog')));
    } catch (e){}

    // parse the current location href
    //     for the query parametes that starts with liveblog.
    //     override those properies over the existing global liveblog obj.
    //     parse only first and second level of the object.
    qs.replace(new RegExp(qsReg.replace('dev[\\]]?', '([^?=&\\.\\]]+)[\\]]?([\\[\\.]([^?=&\\]]+)[\\]\\.]?)?'), 'g'),
        function (match, key, hasSub, subkey, hasEquality, value) {
        value = decodeURIComponent(value);
        if (hasSub) {
            liveblog[key] = liveblog[key] ? liveblog[key] : {};
            liveblog[key][subkey] = hasEquality ? value : true;
        } else {
            liveblog[key] = hasEquality ? value : true;
        }
    });
}

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
        return 'https://' +
                hostname +
                (port && (port !== '80' && port !== '443') ? ':' + port : '');
    });
    return urlString;
};
// fix servers frontend url
liveblog.servers.frontend = liveblog.browserUrl(liveblog.servers.frontend ?
                                                        liveblog.servers.frontend :
                                                        liveblog.servers.rest);
// fix the rest
liveblog.servers.rest = liveblog.browserUrl(liveblog.servers.rest ?
                                                        liveblog.servers.rest :
                                                        liveblog.servers.frontend);

// after aditional properties where added remake the baseUrl for loader and require.
liveblog.baseUrl = liveblog.require.baseUrl = liveblog.servers.frontend + liveblog.paths.scripts;
// min is if we need to load the production files.
liveblog.min = !liveblog.dev || liveblog.emulateprod;

var loadMain = function() {
    if (liveblog.min) {
        // if is the production then object liveblog.require was already setup.
        liveblog.loadJs('build/main');
    } else {
        /*jshint unused:false*/
        // set the require object for development mode.
        window.require = liveblog.require;
        liveblog.loadJs('node_modules/requirejs/require').setAttribute('data-main', liveblog.baseUrl + 'main.js');
    }
};
// this is the callback after the version was loaded.
liveblog.callbackVersion = function(ver) {
    // add version to require urlArgs.
    liveblog.urlArgs = liveblog.require.urlArgs = 'version=' + ver.major + '.' + ver.minor + '.' + ver.revision;
    if (liveblog.delay) {
        setTimeout(loadMain, parseInt(liveblog.delay, 10) * 1000);
    } else {
        loadMain();
    }
};

liveblog.loadJs('version');
