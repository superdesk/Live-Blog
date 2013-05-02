define([
    'backbone',
    'desk/views/task',
    'tmpl!superdesk-desk>desk/status'
], function(Backbone, TaskView) {
    return Backbone.View.extend({
        render: function() {
            $(this.el).tmpl('superdesk-desk>desk/status', this.model.attributes);
            this.renderTasks();
            return this;
        },
    
        renderTasks: function() {
            var list = $(this.el).find('.assignments').empty();
            this.collection.each(function(task) {
                if (task.get('Status').Key === this.model.get('Key')) {
                    var view = new TaskView({model: task});
                    list.append(view.render().el);
                }
            }, this);
        }
    });
});
