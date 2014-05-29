'use strict';

define([
    'lib/require-global',
    'module',
    'underscore',
    'lib/utils'
], function(requirejs, module, _, utils) {
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
        var loadPlugins = function(plugins) {
            _.each(plugins, function(fn, key) {
                fn(config);
            });
            callback();
        },
        themesPathed = (liveblog.min ? module.config().buildPath : module.config().themesPath),
        themesPath = function(path) {
            if (_.isArray(path)) {
                path = path.join('/');
            }
            return themesPathed + path;
        };
        // Add the build to liveblog.paths
        if (liveblog.min) {
            liveblog.paths.build = module.config().buildPath;
            liveblog.paths.themes = module.config().themesPath;
        }
        // Set liveblog theme
        liveblog.theme = liveblog.theme ? liveblog.theme : config.theme;
        if (config.language) {
            liveblog.language = config.language;
        }
        // Set the path for theme template files and theme config file
        requirejs.config({
            paths: {
                theme: themesPath(liveblog.theme),
                themeFile: themesPath(liveblog.theme)
            }
        });
        // Load (apply) theme config
        undefineTheme();
        require([
            'plugins',
            'themeFile',
            'lib/helpers/find-environment',
            'i18n!livedesk_embed'
        ], function(plugins, theme, findEnvironment) {
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
                        theme: themesPath([liveblog.theme, liveblog.environment]),
                        themeFile: themesPath([liveblog.theme, liveblog.environment])
                    }
                });
                requirejs(['plugins', 'themeFile'], function(plugins, theme) {
                    loadPlugins(plugins);
                }, function(err) {
                    undefineTheme();
                    utils.dispatcher.trigger('sub-theme-file.request-failed');
                });
            } else {
                loadPlugins(plugins);
            }
        }, function(err) {
            undefineTheme();
            utils.dispatcher.trigger('theme-file.request-failed');
        });
    };
});
