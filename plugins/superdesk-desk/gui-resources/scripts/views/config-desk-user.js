define(['backbone', 'tmpl!superdesk-desk>list-user'], function(Backbone) {
    return Backbone.View.extend({
        tagName: 'li',

        events: {
            'click .remove': 'destroy'
        },

        render: function() {
            $(this.el).tmpl('superdesk-desk>list-user', this.model.getData());
            return this;
        },

        destroy: function(e) {
            e.preventDefault();
            if (confirm(_("Are you sure you want to remove member?"))) {
                this.model.destroy();
                this.remove();
            }
        }
    });
});
