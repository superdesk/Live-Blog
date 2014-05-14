'use strict';
define([
    'views/base-view',
    'models/liveblog',
    'lib/utils',
    'tmpl!embed-code'
], function(BaseView, Liveblog, utils) {

    return BaseView.extend({
        el: false,
        initialize: function() {
            utils.dispatcher.trigger('initialize.embed-code-view', this);
            this.setTemplate('embed-code');
        },
        serialize: function() {
            return this.model.toJSON();
        }
    });
});
