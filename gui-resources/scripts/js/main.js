'use strict';
require.config({
    config: {
        'load-theme': {
            themesPath:             '../../themes/',
            buildPath:              './build/themes/'
        }
    },
    paths: {
        'jquery':                   'bower_components/jquery/dist/jquery',
        'json2':                    'bower_components/json2/json2',
        'dustjs-linkedin':          'node_modules/dustjs-linkedin/dist/dust-full',
        'dustjs-helpers':           'node_modules/dustjs-helpers/dist/dust-helpers',
        'dust':                     'lib/dust',
        'jed':                      'node_modules/jed/jed',
        'lodash.compat':            'node_modules/lodash/dist/lodash.compat',
        'backbone':                 'node_modules/backbone/backbone',
        'backbone-custom':          'lib/backbone/backbone-custom',
        'backbone.layoutmanager':   'node_modules/backbone.layoutmanager/backbone.layoutmanager',
        'moment':                   'node_modules/moment/min/moment-with-langs',
        'moment-timezone':          'bower_components/moment-timezone/builds/moment-timezone-with-data-2010-2020',
        'waypoints':                'bower_components/jquery-waypoints/waypoints',
        //'font-awesome':             'bower_components/font-awesome/css/font-awesome.min',
        'font-awesome':             '//cdnjs.cloudflare.com/ajax/libs/font-awesome/4.3.0/css/font-awesome.min',
        'themeBase':                '../../themes/base',
        'tmpl':                     'lib/require/tmpl',
        'i18n':                     'lib/require/i18n',
        'css':                      'lib/require/css'
    },
    shim: {
        json2: {
            exports: 'JSON'
        },
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
    }
});

require([
    'jquery',
    'backbone',
    'lib/jquery/xdomainrequest'
], function($, Backbone) {
    $(function() {
        // Router can't be required before liveblog global variable is defined
        require(['router'], function(Router) {
            /*jshint unused: false */
            var router = new Router();
            Backbone.history.start({pushState: false});
        });
    });
});
