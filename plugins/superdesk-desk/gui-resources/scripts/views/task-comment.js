define([
    'backbone',
    'desk/models/task-comment',
    config.guiJs('superdesk/user', 'jquery/avatar'),
    'tmpl!superdesk-desk>list-task-comment'
], function(Backbone, TaskComment) {
    return Backbone.View.extend({
        tagName: 'li',

        events: {
            'click [data-action="edit"]': 'edit',
            'click [data-action="edit-save-comment"]': 'saveComment',
            'click [data-action="edit-discard-comment"]': 'discardComment',
            'click [data-action="delete"]': 'destroy'
        },

        render: function() {
            var data = this.model.getData();
            //$.avatar.setImage(data, {needle: 'User.EMail', size: 36});
            $(this.el).tmpl('superdesk-desk>list-task-comment', data);
            return this;
        },

        // TODO
        edit: function(e) {
            $(this.el).find('.comment-text').hide();
            $(this.el).find('.action-menu').hide();
            $(this.el).find('.edit-comment-box').show();
        },

        // TODO
        saveComment: function(e) {
            var self = this;

            var data = {'Text': $(this.el).find('[data-task-info="edit-comment"]').val()};

            this.model.save(data, {wait: true, patch: true,
                success: function(model) {
                    $(self.el).find('.comment-text').html(data.Text);
                    self.discardComment();
                },
                error: function(model, xhr) {
                    throw xhr;
                }
            });
        },

        // TODO
        discardComment: function(e) {
            $(this.el).find('.comment-text').show();
            $(this.el).find('.action-menu').show();
            $(this.el).find('.edit-comment-box').hide();
        },

        destroy: function(e) {
            var self = this;

            this.model.destroy({success: function(model, response){
                self.el.remove();
            }});
        }
    });
});
