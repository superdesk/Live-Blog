define([
    'backbone',
    'desk/models/task',
    'tmpl!superdesk-desk>edit-task'
], function(Backbone, Task) {
    return Backbone.View.extend({
        events: {
            'click [data-action="close"]': 'close',
            'click [data-action="save"]': 'save'
        },

        initialize: function() {
            if (!this.model) {
                this.model = new Task();
                this.model.set('Desk', this.options.desk.id);
            }

            this.render();
        },

        render: function() {
            $(this.el).tmpl('superdesk-desk>edit-task', this.model.getView());
            $(this.el).appendTo($.superdesk.layoutPlaceholder);
            $(this.el).find('.modal').modal('show');
            return this;
        },

        save: function(e) {
            var data = {
                Title: $(this.el).find('[data-task-info="title"]').val()
            };

            var view = this;
            var isNew = this.model.isNew();
            var tasks = this.options.desk ? this.options.desk.tasks : null;
            this.model.save(data, {wait: true, patch: true,
                success: function(model) {
                    view.close(e);
                    if (isNew) {
                        model.fetch({success: function(model) {
                            tasks.add(model);
                        }});
                    }
                },
                error: function(model, xhr) {
                    throw xhr;
                }
            });
        },

        close: function(e) {
            e.preventDefault();
            $(this.el).find('.modal').modal('hide');
            this.remove();
        }
    });
});
