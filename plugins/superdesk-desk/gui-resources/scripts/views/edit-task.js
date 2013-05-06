define([
    'backbone',
    'desk/models/task',
    'desk/models/task-comment',
    'desk/views/task-comment',
    'tmpl!superdesk-desk>edit-task'
], function(Backbone, Task, TaskComment, TaskCommentView) {
    return Backbone.View.extend({
        events: {
            'click [data-action="close"]': 'close',
            'click [data-action="save"]': 'save',
            'click [data-action="save-comment"]': 'saveComment'
        },

        initialize: function() {
            if (!this.model) {
                this.model = new Task();
                this.model.set('Desk', this.options.desk.id);
            }

            if (!this.model.isNew()) {
                this.model.comments.on('reset', this.renderComments, this);
            }
            
            this.render();
        },

        fetchComments: function() {
            if (!this.model.isNew()) {
                this.model.comments.fetch({headers: this.model.comments.xfilter, reset: true})/*.done(function(){console.log(self.model.comments)})*/;
            }
        },

        renderComments: function() {
            var list = $(this.el).find('.comment-list').empty();
            this.model.comments.each(function(comment) {
                var view = new TaskCommentView({model: comment});
                list.append(view.render().el);
            });
        },

        render: function() {
            $(this.el).tmpl('superdesk-desk>edit-task', this.model.getView());
            $(this.el).appendTo($.superdesk.layoutPlaceholder);
            $(this.el).find('.modal').modal('show');
            this.fetchComments();
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

        saveComment: function(e) {
            var self = this;

            var data = {
                Task: this.model.get('Id'),
                Text: $(this.el).find('[data-task-info="comment"]').val()
            };

            var taskComment = new TaskComment();
            taskComment.save(data, {
                wait: true,
                success: function(model) {
                    $(self.el).find('[data-task-info="comment"]').val('');
                    self.fetchComments();
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
