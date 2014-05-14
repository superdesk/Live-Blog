'use strict';

define([
    'underscore',
    'backbone-custom',
    'dust',
    'lib/utils',
    'backbone.layoutmanager'
], function(_, Backbone, dust, utils) {
    return Backbone.View.extend({
        // Treat all Backbone.View's automatically as
        // (backbone.layoutManager) Layouts.
        manage: true,

        // For a given template file name return the template name registered by dust.
        // Return the current theme template if registered, otherwise return the default
        // base theme template.
        // (ex: for 'container' return 'theme/container' or 'themeBase/container')
        themedTemplate: function(name) {
            return dust.themed(name);
        },

        // Set template view attribute to the current theme template if registered,
        // to base theme template otherwise.
        setTemplate: function(name) {
            this.template = this.themedTemplate(name);
        },

        // Since templates are loaded by Require.js
        // there is no need to 'fetch' them.
        // fetchTemplate just need to return the registered template name.
        fetchTemplate: function(name) {
            return name;
        },

        renderTemplate: function(template, context) {
            // To make it async, call 'async' and store the return value
            // (callback function)
            var done = this.async();

            dust.render(template, context, function(err, out) {
                if (err) {
                    // TODO: What do we want to do with the error?
                    throw err;
                } else {
                    done(out);
                }
            });
        },

        // Get the parent view using backbone.layoutManager __manager__
        parentView: function() {
            return this.__manager__.parent;
        },

        // Fix LB-1564
        // We set some view properties for Backbone.layoutManager to work as
        // if the view had been rendered
        fakeViewRendering: function() {
            this.hasRendered      = true;
            this.__manager__.noel = true;
        },

        events: {},

        // Add events to the view only if we are in the client.
        // Accepts an events object that would extend the existent object.
        clientEvents: function(events) {
            if (utils.isClient) {
                _.extend(this.events, events);
            }
        }
    });
});
