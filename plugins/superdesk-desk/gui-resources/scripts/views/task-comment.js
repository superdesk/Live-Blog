define(['backbone', 'tmpl!superdesk-desk>list-task-comment'], function(Backbone) {
    return Backbone.View.extend({
        tagName: 'li',

        events: {},

        render: function() {
            $(this.el).tmpl('superdesk-desk>list-task-comment', this.model.getView());
            return this;
        },

        destroy: function(e) {
            
        }
    });
});
