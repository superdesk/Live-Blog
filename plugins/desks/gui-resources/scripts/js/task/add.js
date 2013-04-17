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
    DeskTasks = giz.Collection.extend({model: Task, url: new giz.Url('Desk/Task')}),
    deskTasks = new DeskTasks,
    AddView = giz.View.extend
    ({
        events:
        {
            "form": { 'submit': 'save' },
            "[data-action='save']": { 'click': 'save' },
            "[data-list='users'] li": { 'click': 'assign' }
        },
        /*!
         * refresh data on UI
         */
        refreshUIData: function()
        {
            this.refreshTaskList();
            this.refreshAsigneeList();
        },
        /*!
         * 
         */
        refreshTaskList: function()
        {
            var self = this;
            deskTasks.xfilter('*').sync({data: { desk: this.desk.get('id') }}).done(function()
            { 
                $('[data-list="parent-task"]', this.el).html('');
                deskTasks.each(function(){ $('[data-list="parent-task"]', self.el)
                    .append('<li value="'+this.get('Id')+'">'+this.get('Title')+'</li>'); }); 
            });
        },
        /*!
         * 
         */
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
        _assigned: false,
        /*!
         * assign user to task
         */
        assign: function(evt)
        {
            var userId = $(evt.currentTarget).attr('value'),
                self = this;
            $('[data-task-info="assignee-image"]', self.el).html('');
            this.desk.get('User').get(userId).done(function(user)
            { 
                self._assigned = user;
                user.xfilter().sync().done(function()
                { 
                    $('[data-task-info="assignee"]', self.el).removeClass('hide');
                    $('[data-task-info="assignee-name"]', self.el).text(user.get('Name'));
                    user.get('MetaDataIcon').sync({data:{ thumbSize: 'large'}})
                    .done(function()
                    { 
                        $('[data-task-info="assignee-image"]', self.el).html('<img src="'+user.get('MetaDataIcon').get('Thumbnail').href+'" />');
                    })
                    .fail(function(){  }); 
                }); 
            });
            return this;
        },
        setDesk: function(desk)
        {
            this.desk = desk;
            desk.off('read.task').off('update.task')
                .on('read.task', this.refreshUIData, this)
                .on('update.task', this.refreshUIData, this)
                .sync();
            return this;
        },
        activate: function()
        {
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
            $(self.el).tmpl('superdesk/desks>task/add');
        },
        save: function(evt)
        {
            var task = new Task,
                data = 
                {
                    Title: $('[data-task-info="title"]', this.el).val(), 
                    Description: $('[data-task-info="description"]', this.el).html(),
                    Status: $('[data-task-info="status"]', this.el).text(),
                    Desk: this.desk
                };
            if( this._assigned ) data.User = this._assigned;
            task.set(data);
            task.sync().done(function()
            { 
                //console.log(task);
            });
            $('.modal', this.el).modal('hide');
            evt.preventDefault();
        }
    }),
    
    EditView = AddView.extend
    ({ 
        setTask: function(task)
        {
            var self = this;
            this.task = task;
            this.task.sync().done(function(){ self.setDesk(self.task.get('Desk')); });
            return this; 
            // data-task-info="title"
        }
    }),
    
    addView = new AddView,
    editView = new EditView;
    
    var desk = new Desk('http://localhost:8080/resources/Desk/Desk/1'),
        task = new Task('http://localhost:8080/resources/Desk/Task/1');
    
    //return { init: function(){ addView.setDesk(desk).activate(); }};
    return { init: function(){ editView.setTask(task).activate(); }};
});