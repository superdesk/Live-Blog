/* global requirejs */
'use strict';

define([
    'module',
    'underscore',
    'plugins',
    'lib/utils'
], function(module, _, plugins, utils) {
    var undefineTheme = function() {
        requirejs.undef('theme');
        requirejs.undef('themeFile');
    };
    // Set theme and theme file paths.
    // Once the paths are correctly set, load the files,
    //  create the blogView and use it as param for the callback function.
    return function(config, callback) {
        config = config || {theme: 'default'};
        callback = callback || function() {};
        var loadPlugins = function() {
            _.each(plugins, function(fn, key) {
                fn(config);
            });
            callback();
        };
        // Set liveblog theme
        liveblog.theme = liveblog.theme ? liveblog.theme : config.theme;
        if (config.language) {
            liveblog.language = config.language;
        }
        // Set the path for theme template files and theme config file
        require.config({
            paths: {
                theme: module.config().themesPath + liveblog.theme,
                themeFile: module.config().themesPath + liveblog.theme
            }
        });
        // Load (apply) theme config
        undefineTheme();
        require([
            'themeFile',
            'lib/helpers/find-environment',
            'i18n!livedesk_embed'
        ], function(theme, findEnvironment) {
            // If the theme has different environments reset the
            //  path to theme template files and theme config file to use
            //  the ones for the selected environment
            if (theme && theme.environments) {
                if (!liveblog.environment) {
                    var environment = findEnvironment();
                    liveblog.environment = theme.environments[environment] ?
                        theme.environments[environment] : theme.environments['default'];
                }
                undefineTheme();
                requirejs.config({
                    paths: {
                        theme: module.config().themesPath + liveblog.theme + '/' + liveblog.environment,
                        themeFile: module.config().themesPath + liveblog.theme + '/' + liveblog.environment
                    }
                });
                requirejs(['themeFile'], function() {
                    loadPlugins();
                }, function(err) {
                    undefineTheme();
                    utils.dispatcher.trigger('sub-theme-file.request-failed');
                });
            } else {
                loadPlugins();
            }
        }, function(err) {
            undefineTheme();
            utils.dispatcher.trigger('theme-file.request-failed');
        });
    };
});
