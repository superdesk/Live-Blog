define
([
    'jquery',
    'gizmo/superdesk',
    'gizmo/superdesk/action',
    config.guiJs('superdesk/desks', 'models/desk'),
    config.guiJs('superdesk/desks', 'models/task'),
    config.guiJs('superdesk/desks', 'models/task-status'),
    'tmpl!superdesk/desks>task/add'
],
function($, giz, Action, Desk, Task, TaskStatus)
{
    var
    AddView = giz.View.extend
    ({
        events:
        {
            "form": { 'submit': 'save' },
            "[data-action='save']": { 'click': 'save' }
        },
        refreshAsigneeList: function()
        {
            var users = this.desk.get('User'),
                self = this;
            users.xfilter('*').sync().done(function()
            { 
                $('[data-list="users"]', self.el).html('');
                users.each(function(){ $('[data-list="users"]', self.el)
                    .append('<li value="'+this.get('Id')+'">'+this.get('Name')+'</li>'); }); 
            });
        },
        activate: function(desk)
        {
            if( desk )
            {
                this.desk = desk;
                desk.off('read.task').off('update.task')
                    .on('read.task', this.refreshAsigneeList, this)
                    .on('update.task', this.refreshAsigneeList, this)
                    .sync();
            }
            
            
            $(this.el).appendTo($.superdesk.layoutPlaceholder);
            $('.modal', this.el).modal();
            $('input', this.el).val('');
        },
        updateStatus: function()
        {
            $('[data-task-info="status"]', this.el).text(this.statuses._list[0].get('Key'));
        },
        init: function()
        {
            this.statuses = new (giz.Collection.extend({model: TaskStatus}))(TaskStatus.prototype.url.get());
            this.statuses.off('read.task').off('update.task')
                .on('read.task', this.updateStatus, this)
                .on('update.task', this.updateStatus, this)
                .xfilter('*').sync();
            
            this.render();
        },
        render: function()
        {
            var self = this;
            $(self.el).tmpl('superdesk/desks>task/add', function(){  });
        },
        save: function(evt)
        {
            var task = new Task;
            task.set({Title: $('[data-task-info="title"]', this.el).val(), Description: $('[data-task-info="description"]', this.el).html()});
            console.log(task);
            evt.preventDefault();
            this.el.modal('hide');
        }
    }),
    
    addView = new AddView;
    
    var desk = new Desk('http://localhost:8080/resources/Desk/Desk/1');
    
    return { init: function(){ addView.activate(desk); }};
});