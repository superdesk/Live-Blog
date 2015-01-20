require.config({
    shim: {
        'typekitFont': {
            'exports': 'Typekit'
        }
    }
});
define([
    'backbone',
    'plugins',
    'lib/utils'
], function (Backbone, plugins, utils) {
    'use strict';
    plugins.typekit = function (config) {
        if (utils.isClient) {
            require(['typekitFont'], function (Typekit) {
                Backbone.$(function() { try {Typekit.load();}catch (e){}});
            });
        }
    };
    return plugins.typekit;
});
