// Liveblog custom additions to Backbone.js
'use strict';

define([
    'backbone',
    'underscore'
], function(Backbone, _) {

    Backbone.defaultSync = Backbone.sync;

    Backbone.sync = function(method, model, options) {

        if (!options) { options = {}; }

        // Never delete models from the collection on merge
        options.remove = false;

        if (method === 'read') {
            // Request a date format that all browsers can parse
            options.headers = _.isObject(options.headers) ? options.headers : {};

            options.headers['X-Format-DateTime'] = 'yyyy-MM-ddTHH:mm:ss\'Z\'';
            // Add parameters provided in model.syncParams.headers
            // to the request header
            _.each(model.syncParams.headers, function(value, key) {
                options.headers[key] = value;
            });

            // Add parameters provided in model.syncParams.data
            // as parameters to the request url, unless the same
            // parameter has been provided as an option in fetch method.
            // (params in fetch method have precedence over params in
            // syncParams.data)
            _.each(model.syncParams.data, function(value, key) {
                options.data = options.data || {};
                if (!options.data[key]) {
                    options.data[key] = value;
                }
            });
        }
        return Backbone.defaultSync(method, model, options);
    };

    Backbone.defaultAjax = Backbone.ajax;

    Backbone.ajax = function(options) {

        if (typeof process !== 'undefined' &&
                process.versions &&
                !!process.versions.node) {
            return Backbone.nodeSync(options);
        }

        // send the old headers if liveblog.emulateOLDHEADERS
        if (liveblog.emulateOLDHEADERS) {
            options.dataType = 'json';
            options.headers = _.isObject(options.headers) ? options.headers : {};
            options.headers.Accept = 'text/json';
        }

        // send the headers as GET parametes if liveblog.emulateHEADERSPARAMS
        if (liveblog.emulateHEADERSASPARAMS) {
            options.data = _.extend(options.data, options.headers);
            delete options.headers;
        }
        return Backbone.defaultAjax(options);
    };

    Backbone.nodeSync = function(options) {

        var request = require.nodeRequire('request'),
           qs = require.nodeRequire('qs');

        // Parse response to json
        options.json = true;
        options.timeout = 1000;

        // Set the query string with the options.data params
        if (options.data) {
            options.url += ((options.url.indexOf('?') === -1) ? '?': '&') + qs.stringify(options.data);
            delete options.data;
        }

        if (GLOBAL && GLOBAL.liveblogLogger) {
            liveblogLogger.info('Request to url: %s', options.url);
        }
        // Use options.success and options.errors callbacks
        request.get(options, function(error, response, data) {
            if (!error && response.statusCode === 200) {
                if (options.success) {
                    return options.success(data);
                }
            } else if (options.error && _.has(response, 'request')) {
                liveblogLogger.error('Request to url: %s failed with code: %s and body: ', response.request.href, response.statusCode, response.body);
                return options.error(response);
            }
        });
    };

    return Backbone;
});
