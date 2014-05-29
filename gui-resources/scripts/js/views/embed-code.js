'use strict';

define([
    'views/base-view',
    'models/liveblog',
    'lib/utils',
    'tmpl!embed-code'
], function(BaseView, Liveblog, utils) {

    return BaseView.extend({

        // Set `el` to the top level element from the template
        // instead of the default behaviour of inserting a `div` element
        // (Backbone.LayoutManager).
        el: false,

        initialize: function() {
            utils.dispatcher.trigger('initialize.embed-code-view', this);
            this.setTemplate('embed-code');
        },

        // Backbone.LayoutManager `serialize`.
        serialize: function() {
            return this.model.toJSON();
        }
    });
});
