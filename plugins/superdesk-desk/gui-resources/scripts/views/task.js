define([
    'backbone',
    'desk/views/edit-task',
    'tmpl!superdesk-desk>desk/task'
], function(Backbone, EditTaskView) {
    return Backbone.View.extend({
        tagName: 'li',

        events: {
            'click .assign-description': 'edit'
        },

        initialize: function() {
            this.listenTo(this.model, 'change', this.render);
        },

        render: function() {
            $(this.el).tmpl('superdesk-desk>desk/task', this.model.attributes);
            return this;
        },

        edit: function() {
            new EditTaskView({model: this.model});
        }
    });
});
