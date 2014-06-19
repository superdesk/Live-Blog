define([
    'backbone',

    'tmpl!superdesk-desk>select-user'
], function(Backbone) {
    return Backbone.View.extend({
        tagName: 'li',

        events: {
            'change input:checkbox': 'toggle'
        },

        initialize: function() {
            this.model.on('change', this.render, this);
        },

        render: function() {
            $(this.el).tmpl('superdesk-desk>select-user', this.model.getData());
            return this;
        },

        toggle: function() {
            this.model.set('selected', !this.model.get('selected'));
        }
    });
});
