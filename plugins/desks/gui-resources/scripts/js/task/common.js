define
([
    'jquery',
    'gizmo/superdesk',
    'moment',
    'gizmo/superdesk/action',
    config.guiJs('superdesk/desks', 'models/desk'),
    config.guiJs('superdesk/desks', 'models/task'),
    config.guiJs('superdesk/desks', 'models/task-status'),
    'jqueryui/datepicker',
    'tmpl!superdesk/desks>task/add-edit'
],
function($, giz, Action, Desk, Task, TaskStatus)
{
    var dpH4xx = $.datepicker._updateDatepicker;
    $.datepicker._updateDatepicker = function()
    {
        dpH4xx.apply(this, arguments);
        if( !this.dpDiv.find('[data-dp="time"]').length )
        {
            this.dpDiv.append
            ('<div data-dp="time">'+
                '<div class="input-append pull-left">'+
                    '<input class="span1" data-dp="hours" type="text" />'+
                    '<span class="add-on">hours</span>'+
                '</div>'+
                '<div class="input-append pull-left">'+
                    '<input class="span1" data-dp="minutes" type="text" />'+
                    '<span class="add-on">minutes</span>'+
                '</div>'+
            '</div>');
        }
    };
    
    var 
    DeskTasks = giz.Collection.extend({model: Task, url: new giz.Url('Desk/Task')}),
    deskTasks = new DeskTasks,
    AddView = giz.View.extend
    ({
        events:
        {
            "form": { 'submit': 'save' },
            "[data-action='save']": { 'click': 'save' },
            "[data-list='users'] li": { 'click': 'assign' },
            "[data-ctrl='due-date-proxy']": { 'click': 'dueDate' },
            "[data-ctrl='add-subtask']": { 'click': 'save' }
        },
        
        dueDate: function()
        {
            $("input[data-task-info='due-date']", this.el).trigger('focus');
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
            $(self.el).tmpl('superdesk/desks>task/add-edit', function()
            {
                $("input[data-task-info='due-date']", self.el).datepicker
                ({ 
                    dateFormat: "yy-mm-dd",
                    onClose: function(dateText, inst)
                    {
                        dateText += " "
                            +($('[data-dp="hours"]', $(inst.dpDiv)).val()||'00')+':'
                            +($('[data-dp="minutes"]', $(inst.dpDiv)).val()||'00')+':00';
                        $(this).val(moment(dateText).calendar());
                        $('[data-task-info="'+$(this).attr('data-task-info')+'"]', self.el).text($(this).val());
                    }
                }); 
            });
        },
        save: function(evt)
        {
            var task = this.task || new Task,
                data = 
                {
                    Title: $('[data-task-info="title"]', this.el).val(), 
                    Description: $('[data-task-info="description"]', this.el).html(),
                    Status: $('[data-task-info="status"]', this.el).text(),
                    Desk: this.desk.get('Id'),
                    DueDate: $("input[data-task-info='due-date']", this.el).val()
                };
            if( this._assigned ) data.User = this._assigned;
            task.set(data);
            task.sync().done(function()
            { 
                if( $(evt.currentTarget).is('[data-ctrl="add-subtask"]') );
                //console.log(task);
            });
            $('.modal', this.el).modal('hide');
            evt.preventDefault();
        }
    }),
    
    EditView = AddView.extend
    ({ 
        /*!
         * refresh data on UI
         */
        refreshUIData: function()
        {
            this.refreshTaskInfo();
            this.refreshTaskList();
            this.refreshAsigneeList();
        },
        /*!
         * 
         */
        refreshTaskInfo: function()
        {
            $('[data-task-info="title"]', this.el).val(this.task.get('Title'));
            $('[data-task-info="description"]', this.el).html(this.task.get('Description'));
        },
        setTask: function(task)
        {
            var self = this;
            this.task = task;
            this.task.sync().done(function(){ self.setDesk(self.task.get('Desk')); });
            return this; 
        }
    });
    
    return { add: AddView, edit: EditView };
    
    //return { init: function(){ addView.setDesk(desk).activate(); }};
    //return { init: function(){ editView.setTask(task).activate(); }};
});