'use strict';

var allTestFiles = [];
var TEST_REGEXP = /(spec|test)\.js$/i;

//var pathToModule = function(path) {
    //return path.replace(/^\/base\//, '').replace(/\.js$/, '');
//};

Object.keys(window.__karma__.files).forEach(function(file) {
    if (TEST_REGEXP.test(file)) {
        // Normalize paths to RequireJS module names.
        // Commented this next line because it applies require.config.baseUrl
        // to test path
        //allTestFiles.push(pathToModule(file));
        allTestFiles.push(file);
    }
});

require.config({
    // Karma serves files under /base, which is the basePath from your config file
    baseUrl: '/base/gui-resources/scripts/js/',

    // dynamically load all test files
    deps: allTestFiles,

    //config: {
        //'load-theme': {
            //themesPath:             '../../../themes/'
        //},
        //css: {
            //host: '//' + liveblog.hostname + (liveblog.port ? (':' + liveblog.port) : '') + '/content/lib/livedesk-embed'
        //}
    //},

    paths: {
        'jquery':                   'bower_components/jquery/dist/jquery.min',
        'json2':                    'bower_components/json2/json2',
        'dustjs-linkedin':          '../../../node_modules/dustjs-linkedin/dist/dust-full.min',
        'dustjs-helpers':           '../../../node_modules/dustjs-helpers/dist/dust-helpers.min',
        'dust':                     'lib/dust',
        'jed':                      '../../../node_modules/jed/jed',
        'lodash.compat':            '../../../node_modules/lodash/dist/lodash.compat.min',
        'backbone':                 '../../../node_modules/backbone/backbone-min',
        'backbone-custom':          'lib/backbone/backbone-custom',
        'backbone.layoutmanager':   '../../../node_modules/backbone.layoutmanager/backbone.layoutmanager',
        'moment':                   '../../../node_modules/moment/min/moment.min',
        'themeBase':                '../../../gui-themes/themes/base',
        'tmpl':                     'lib/require/tmpl'
        //'i18n':                     'lib/require/i18n',
        //'css':                      'lib/require/css'
    },

    shim: {
        //json2: {
            //exports: 'JSON'
        //},
        'dustjs-linkedin': {
            exports: 'dust'
        },
        'dustjs-helpers': {
            deps: ['dustjs-linkedin']
        }
    },
    map: {
        '*': {
            'underscore':   'lib/lodash-private',
            'lodash':       'lib/lodash-private',
            'jquery':       'lib/jquery-private',
            'backbone':     'lib/backbone-private'
        },
        'lib/jquery-private':   {'jquery': 'jquery'},
        'lib/backbone-private': {'backbone': 'backbone'},
        'lib/lodash-private':   {'lodash': 'lodash.compat'}
    },

    // we have to kickoff jasmine, as it is asynchronous
    callback: window.__karma__.start
});
