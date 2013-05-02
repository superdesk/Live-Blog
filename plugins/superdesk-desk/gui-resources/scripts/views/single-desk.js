define([
    'backbone',
    'desk/views/board',
    'desk/views/edit-task',
    'tmpl!superdesk-desk>desk/single'
], function(Backbone, BoardView, EditTaskView) {
    return Backbone.View.extend({
        events: {
            'click #add-task': 'addTask'
        },

        initialize: function() {
            this.listenTo(this.model, 'change', this.render);
        },

        render: function() {
            $(this.el).tmpl('superdesk-desk>desk/single', this.model.attributes);
            this.listenTo(this.model.tasks, 'reset', this.renderBoards);
            this.listenTo(this.model.tasks, 'add', this.renderBoards);
            this.model.tasks.fetch({reset: true, headers: this.model.tasks.xfilter});
            return this;
        },

        renderBoards: function() {
            var list = $(this.el).find('.desk-horizontal-scroll').empty();
            this.model.boards.each(function(board) {
                var view = new BoardView({model: board, collection: this.model.tasks, desk: this.model});
                list.append(view.render().el);
            }, this);
        },

        addTask: function() {
            new EditTaskView({desk: this.model});
        }
    });
});
