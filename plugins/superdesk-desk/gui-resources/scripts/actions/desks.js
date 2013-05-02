define([
    'jquery',
    'backbone',
    'router',
    'desk/models/desk',
    'desk/models/desk-collection',
    'desk/models/task-status-collection',
    'desk/views/single-desk'
],function($, Backbone, router, Desk, DeskCollection, TaskStatusCollection, SingleDeskView) {
    var DeskMenuView = Backbone.View.extend({
        tagName: 'li',
        render: function() {
            var link = $('<a />').text(this.model.get('Name')).attr('href', '#desks/' + this.model.id);
            $(this.el).html(link);
            return this;
        }
    });

    var MenuView = Backbone.View.extend({
        initialize: function() {
            this.collection.on('reset', this.render, this);
        },

        render: function() {
            var list = $(this.el).empty();
            this.collection.each(function(desk) {
                var view = new DeskMenuView({model: desk});
                list.append(view.render().el);
            });
        }
    });

    var boards = new TaskStatusCollection([
            {Id: 'todo', Key: 'to do', Name: _('To Do')},
            {Id: 'inprogress', Key: 'in progress', Name: _('In Progress')},
            {Id: 'done', Key: 'done', Name: _('Done')}
        ]);

    router.route('desks/:id', 'desk', function singleDesk(id) {
        var desk = new Desk({Id: id});
        var view = new SingleDeskView({collection: boards, model: desk, el: '#area-main'});
        desk.fetch();
    });

    router.route('desks', 'desks', function allDesks() {
        alert('all');
    });

    return {
        init: function(submenu, menu, data) {
            var desks = new DeskCollection();
            var menu = new MenuView({el: submenu, collection: desks});
            var timeout = 5000;

            var fetchDesks = function fetchDesks() {
                desks.fetch({reset: true, headers: desks.xfilter});
                setTimeout(fetchDesks, timeout);
            };

            desks.xfilter = {'X-Filter': 'Id, Name'};
            fetchDesks();
        }
    };
});
