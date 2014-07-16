'use strict';

var grunt = require('grunt'),
    fs = require('fs'),
    _ = require('lodash');

var makePath = function(base, path) {
        if (_.isArray(path)) {
            path = path.join('/');
        }
        return base + path;
    },
    nodePath = function(path) {
        return makePath('<%= requirejs.main.paths.root %><%= paths.nodeModules %>', path);
    },
    themesPath = function(path, noroot) {
        var base = '<%= paths.themes %>';
        if (!noroot) {
            base = '<%= requirejs.main.paths.root %>' + base;
        }
        return makePath(base, path);
    },
    outPath = function(path) {
        return makePath('<%= paths.build  %>', path);
    },
    scriptsPath = function(path) {
        return makePath('<%= paths.scripts  %>', path);
    };

var defaultOptions = {
    paths: {
        'themeBase':                themesPath('base'),
        'tmpl':                     'lib/require/tmpl',
        'i18n':                     'lib/require/i18n',
        'dust':                     'lib/dust',
        'css':                      'lib/require/css',
        'css-build':                'lib/require/css-build',
        'backbone-custom':          'lib/backbone/backbone-custom',
        'waypoints':                'bower_components/jquery-waypoints/waypoints',
        'dustjs-linkedin':          nodePath('dustjs-linkedin/dist/dust-full'),
        'dustjs-helpers':           nodePath('dustjs-helpers/dist/dust-helpers'),
        'jed':                      nodePath('jed/jed'),
        'lodash.compat':            nodePath('lodash/dist/lodash.compat'),
        'backbone':                 nodePath('backbone/backbone'),
        'backbone.layoutmanager':   nodePath('backbone.layoutmanager/backbone.layoutmanager'),
        'moment':                   nodePath('moment/min/moment-with-langs'),
        'moment-timezone':          'bower_components/moment-timezone/builds/moment-timezone-with-data-2010-2020',
        'require-lib':              nodePath('requirejs/require'),
        'underscore':               nodePath('lodash/dist/lodash.compat'),
        'twitterWidgets':           'empty:'
    },
    namespace: 'liveblog',
    optimize: 'uglify2',
    findNestedDependencies: true,
    preserveLicenseComments: false
    // Add this later when closure will be supported on nodejs.
    // optimize: 'closure',
    // closure: {
    //     CompilerOptions: {
    //         prettyPrint: true
    //     },
    //     CompilationLevel: 'ADVANCED_OPTIMIZATIONS',
    //     loggingLevel: 'WARNING'
    // }
},
task = {
    main: {
        paths: {
            root: '../../../'
        },
        options: {
            mainConfigFile: scriptsPath('main.js'),
            baseUrl: scriptsPath('/'),
            name: 'main',
            out: outPath('main.js'),
            paths: {
                'themeFile':                'empty:'
            },
            include: [
                'css',
                'require-lib'
            ]
        }
    }
};
_.merge(task.main.options, defaultOptions);
var dir = 'gui-themes/themes',
    themes = [],
    theme, subtheme;
// Get all themes and subthemes from the file system.
//   it checks for the *.js in the folder
_.each(fs.readdirSync(dir), function(name) {
    if (name.indexOf('.js') > 0) {
        theme = name.substring(0, name.length - 3);
        themes.push(theme);
        if (!fs.existsSync(dir + '/' + theme)) {
            grunt.log.debug('is not a directory: ', dir + '/' + theme);
        } else {
            _.each(fs.readdirSync(dir + '/' + theme), function(subname) {
                if (subname.indexOf('.js') > 0) {
                    subtheme = subname.substring(0, subname.length - 3);
                    themes.push(theme + '/' + subtheme);
                }
            });
        }
    }
});

_.each(themes, function(theme) {
    task[theme] = {
        options: {
            paths: {
                'theme':                    themesPath(theme),
                'themeFile':                themesPath(theme),
                'jquery':                   'empty:'
            },
            shim: {
                'dustjs-linkedin': {
                    exports: 'dust'
                },
                'dustjs-helpers': {
                    deps: ['dustjs-linkedin']
                }
            },
            excludeShallow: [
                'css',
                'underscore',
                'jed',
                'tmpl',
                'dustjs-linkedin',
                'dustjs-helpers',
                'dust',
                'dust/dust',
                'dust/core',
                'dust/themed',
                'dust/render-themed',
                'dust/helpers/i18n',
                'dust/helpers/trim',
                'dust/helpers/date',
                'dust/helpers/twitter',
                'backbone-custom',
                'backbone.layoutmanager',
                'backbone',
                'moment',
                'lib/utils',
                'lib/gettext',
                'lib/require/i18n-parse',
                'lib/helpers/object-parse',
//                'lib/helpers/visibility-toggle',
                'lib/helpers/display-toggle',
//                'lib/helpers/fixed-encodeURIComponent',
                'lib/helpers/trim-tag',
                'lib/poller',
                'lib/backbone/model-collection-common',
                'tmpl!themeBase/item/base',
                'models/base-model',
                'models/post',
                'models/blog',
                'models/liveblog',
                'collections/base-collection',
                'collections/posts',
                'views/base-view',
                'config/defaultPaginationParams'
            ],
            baseUrl: scriptsPath('/'),
            mainConfigFile: themesPath(theme + '.js', true),
            name: 'themeFile',
            out:  outPath(['themes', theme + '.js'])
        }
    };
    _.merge(task[theme].options, defaultOptions);
});
module.exports = task;
