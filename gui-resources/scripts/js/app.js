'use strict';

var requirejs     = require('./lib/nodejs/requirejs-clear-cache'),
    path          = require('path'),
    fs            = require('fs'),
    Logger        = require('./lib/logger'),
    urlHref       = require('./lib/nodejs/url-href'),
    grunt         = require('grunt'),
    lodash        = require('lodash'),
    dust          = require('./lib/nodejs/dust-clear-cache');

var config = {
        paths: {
            root: '../../../'
        }
    };
config = lodash.merge(grunt.file.readJSON(path.join(__dirname, config.paths.root, 'config.json')), config);
// parse the grunt configuration style to an proper obj.
grunt.initConfig(config);

config = grunt.config.get();
// prase the nodejs property to a url object.
//   so that we can have the port, protocol and hostname for later use.
config.paths.logs = path.join(__dirname, config.paths.logs);

// Create logger for the app
fs.exists(config.paths.logs, function(exists) {
    if (exists) {
        var logFile = fs.createWriteStream(path.join(config.paths.logs, config.logging.nodejs),
                                            {'flags': 'a'});
        GLOBAL.liveblogLogger = new Logger('info', logFile);
    } else {
        console.log(config.paths.log + ' folder missing, to create it run ' +
                        '"grunt create-logs-folder" or "grunt server"');
    }
});

requirejs.config({
    baseUrl: __dirname,
    config: {
        'load-theme': {
            themesPath: path.join(__dirname, config.paths.themes)
        },
        'css': {
            siteRoot: config.paths.themesRoot
        }
    },
    paths: {
        'backbone-custom':      'lib/backbone/backbone-custom',
        layout:                 '../../layout',
        'embed-code':           '../../embed-code',
        dust:                   'lib/dust',
        tmpl:                   'lib/require/tmpl',
        i18n:                   'lib/require/i18n',
        themeBase:              config.paths.themes + '/base',
        'lodash.compat':        config.paths.nodeModules + '/lodash/dist/lodash.compat',
        'moment':               config.paths.nodeModules + '/moment/min/moment-with-langs',
        'moment-timezone':      'bower_components/moment-timezone/builds/moment-timezone-with-data-2010-2020',
        'css':                  'lib/require/css'
    },
    map: {
        '*': {
            'underscore': 'lodash.compat',
            'lodash': 'lodash.compat'
        }
    },
    nodeRequire: require
});

requirejs.onError = function(err) {
    var failedId = err.requireModules && err.requireModules[0];
    requirejs.undef(failedId);
};

GLOBAL.liveblog = lodash.clone(JSON.parse(process.env.liveblog));
GLOBAL.liveblog.browserUrl = urlHref.browserUrl;
requirejs.clearCache('^(css|i18n!|tmpl!theme\/|theme|themeFile|plugins)');
dust.clearCache('^(theme\/)');
requirejs([
    'views/layout',
    'lib/utils'
], function(Layout, utils) {
    var sent = false;
    // if this will work in the future it will be good.
    //   removeing all namespaced events.
    //utils.dispatcher.off('.request-failed');
    utils.dispatcher.off('theme-file.request-failed');
    utils.dispatcher.off('blog-model.request-failed');
    utils.dispatcher.once('blog-model.request-failed', function() {
        if (!sent) {
            sent = true;
            console.log(JSON.stringify({code: 400, body: 'Request for blog has failed.'}));
        }
    });
    utils.dispatcher.once('theme-file.request-failed', function() {
        if (!sent) {
            sent = true;
            console.log(JSON.stringify({code: 400, body: 'Request for theme file has failed.'}));
        }
    });
    var layout = new Layout();
    layout.blogModel.get('publishedPosts').on('sync', function() {
        if (!sent) {
            sent = true;
            // by default cheerio is decoding html value attributes.
            // assume that this is right.
            // ex: syle="background:'url(image)'" became syle="background:&apos;url(image)&apos;"
            layout.$el.options.decodeEntities = false;
            console.log(JSON.stringify({code: 200, body: layout.render().$el.html()}));
        }
    });
}, function(err) {
    console.log(JSON.stringify({code: 400, body: err}));
});
