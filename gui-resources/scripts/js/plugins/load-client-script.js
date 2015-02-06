define([
    'plugins',
    'lib/utils'
], function (plugins, utils) {
    'use strict';
    plugins.loadClientScript = function (config) {
        if (utils.isClient) {
            require(['loadClientScriptUrl']);
        }
    };
    return plugins.loadClientScript;
});
