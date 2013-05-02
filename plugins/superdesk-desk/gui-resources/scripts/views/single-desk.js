define([
    'backbone',
    'desk/views/board',
    'desk/views/edit-task',
    'tmpl!superdesk-desk>desk/single'
], function(Backbone, BoardView, EditTaskView) {
    return Backbone.View.extend({
        events: {
            'click #add-task': 'addTask',
            'click #compact-view': 'toggleCompact',
            'click #list-view': 'listView',
            'click #grid-view': 'gridView'
        },

        initialize: function() {
            this.listenToOnce(this.model, 'change', this.renderOnce);

            this.viewModel = new Backbone.Model({compact: false, list: ''});
            this.listenTo(this.viewModel, 'change', this.render);
        },

        renderOnce: function() {
            this.render();
            this.listenTo(this.model.tasks, 'reset', this.renderBoards);
            this.listenTo(this.model.tasks, 'add', this.renderBoards);
            this.model.tasks.fetch({reset: true, headers: this.model.tasks.xfilter});
            return this;
        },

        render: function() {
            $(this.el).tmpl('superdesk-desk>desk/single', {model: this.model.toJSON(), view: this.viewModel.toJSON()});
            this.renderBoards();
            return this;
        },

        renderBoards: function() {
            var list = $(this.el).find('.desk-horizontal-scroll').empty();
            this.model.boards.each(function(board) {
                var view = new BoardView({model: board, collection: this.model.tasks});
                list.append(view.render().el);
            }, this);
        },

        addTask: function() {
            new EditTaskView({desk: this.model});
        },

        toggleCompact: function(e) {
            e.preventDefault();
            this.viewModel.set('compact', !this.viewModel.get('compact'));
        },

        listView: function(e) {
            e.preventDefault();
            this.viewModel.set('list', 'desk-list');
        },

        gridView: function(e) {
            e.preventDefault();
            this.viewModel.set('list', '');
        }
    });
});
