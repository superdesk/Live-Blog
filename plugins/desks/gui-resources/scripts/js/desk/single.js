define
([
    'jquery',
    'gizmo/superdesk',
    'gizmo/superdesk/action',
    config.guiJs('superdesk/desks', 'models/desk'),
    config.guiJs('superdesk/desks', 'models/task'),
    config.guiJs('superdesk/desks', 'models/task-status'),
    'tmpl!superdesk/desks>desk/single'
],
function($, giz, Action, Desk, Task, TaskStatus)
{

    var
    DeskTasks = giz.Collection.extend({model: Task, url: new giz.Url('Desk/Desk/1/Task')}),
    deskTasks = new DeskTasks;
    deskTasks.sync();

    console.log('desks ', deskTasks);

    SingleView = giz.View.extend({
        init: function()
        {
            console.log('single init');
            this.render();
        },
        render: function() {
            var self = this;
            $(self.el).tmpl('superdesk/desks>desk/single');
            $('#area-main').html($(self.el));
        }
    });
    var singleView = new SingleView;
	return	{init: function(){ 

    }}
});