define
([
    'jquery',
    'gizmo/superdesk',
    'gizmo/superdesk/action',
    config.guiJs('superdesk/desks', 'models/desk'),
    config.guiJs('superdesk/desks', 'models/task'),
    config.guiJs('superdesk/desks', 'models/task-status'),
    'moment',
    'jqueryui/datepicker',
    'tmpl!superdesk/desks>task/add-edit',
    'tmpl!superdesk/desks>task/subtask'
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
    
    taskStatuses = new (giz.Collection.extend({model: TaskStatus}))(TaskStatus.prototype.url.get()),
    
    SubTaskView = giz.View.extend
    ({
        tagName: 'li',
        render: function()
        { 
            var self = this;
            $(self.el).tmpl('superdesk/desks>task/subtask', this.model.feed(), function(e, o)
            { 
                var dd = $('[data-subtask-info="due-date"]', self.el);
                if( dd.text().length ) dd.text(moment(dd.text()).calendar());
            }); 
            return this;
        }
    }),
    
    AddView = giz.View.extend
    ({
        task: null,
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
        /*!
         * set desk model
         */
        setDesk: function(desk)
        {
            this.desk = desk;
            var self = this;
            desk.off('read.task').off('update.task')
                .on('read.task', this.refreshUIData, this)
                .on('update.task', this.refreshUIData, this)
                .sync()
                .done(function(){ self.render(); });
            return this;
        },
        /*!
         * 
         */
        setParent: function(task)
        {
            var updParent = function()
            {
                var parentEl = $('[data-task-info="parent"]', this.el);
                if( parentEl.length )
                    parentEl.text( this.parentTask.get('Title') );
            };
            this.parentTask = task;
            task.off('read.task').off('update.task')
                .on('read.task', updParent, this)
                .on('update.task', updParent, this)
                .sync();
            return this;
        },
        
        _renderShouldOpenModal: false,
        activate: function()
        {
            $(this.el).appendTo($.superdesk.layoutPlaceholder);
            $('.modal', this.el).length && $('.modal', this.el).modal();
            if( !$('.modal', this.el).length ) this._renderShouldOpenModal = true;
            $('input', this.el).val('');
        },
        updateStatus: function()
        {
            // couldn't use .get() because there's no href and I can't overwrite .getHash() :(
            this._defaultStatus = taskStatuses._list[0]; 
        },
        init: function()
        {
            taskStatuses.off('read.task').off('update.task')
                .on('read.task', this.updateStatus, this)
                .on('update.task', this.updateStatus, this)
                .xfilter('*').sync();
        },
        /*!
         * make dates sexy on the view
         * @param string dateText parsable date string
         */
        prettyDate: function(dateText)
        {
            var dueDate = $('[data-task-info="due-date"]', this.el);
            dueDate.text(moment(dateText||dueDate.text()||new Date).calendar()); 
        },
        /*!
         * data to pass to the template
         */
        templateData: function(){ return {}; },
        /*!
         * 
         */
        render: function()
        {
            var self = this;
            $(self.el).tmpl('superdesk/desks>task/add-edit', this.templateData(), function()
            {
                // functionality for due date 
                $("input[data-task-info='due-date']", self.el).datepicker
                ({ 
                    dateFormat: "yy-mm-dd",
                    onClose: function(dateText, inst)
                    {
                        dateText += " "
                            +($('[data-dp="hours"]', $(inst.dpDiv)).val()||'00')+':'
                            +($('[data-dp="minutes"]', $(inst.dpDiv)).val()||'00')+':00';
                        $(this).val(dateText);
                        self.prettyDate(dateText);
                    }
                });
                if( self.parentTask ) $('[data-task-info="parent"]', self.el).text(self.parentTask.get('Title'));
                self.prettyDate();
                if( self._renderShouldOpenModal ) $('.modal', self.el).modal();
            });
        },
        /*!
         * 
         */
        save: function(evt)
        {
            var self = this,
                task = this.task || new Task,
                status = task.get('Status'),
                data = 
                {
                    Title: $('[data-task-info="title"]', this.el).val()||' ', 
                    Description: $('[data-task-info="description"]', this.el).html(),
                    Status: status ? status.get('Key') : this._defaultStatus.get('Key'),
                    Desk: this.desk.get('Id'),
                    DueDate: $("input[data-task-info='due-date']", this.el).val()
                };
            if( this._assigned ) data.User = this._assigned;
            if( this.parentTask ) data.Parent = this.parentTask.get('Id');
            task.set(data);
            task.sync().done(function()
            { 
                if( $(evt.currentTarget).is('[data-ctrl="add-subtask"]') )
                    (new AddView).setParent(task).setDesk(self.desk).activate();
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
        subTasks: function()
        {
            var subtasks = this.task.get('Task'),
                self = this;
            $('[data-list="subtasks"]', self.el).html('');
            subtasks.xfilter('*').sync().done(function()
            {
                subtasks.each(function(){ (new SubTaskView({model: this})).render().el.appendTo($('[data-list="subtasks"]', self.el)); });
                $('[data-task-info="subtask-count"]', self.el).text(subtasks.count());
            });
        },
        setTask: function(task)
        {
            var self = this;
            this.task = task;
            this.task.xfilter('Parent.*').sync().done(function()
            {
                self.setDesk(self.task.get('Desk'));
                self.subTasks();
            });
            return this; 
        },
        templateData: function()
        {
            return this.task.feed();
        }
    });
    
    return { add: AddView, edit: EditView };
    
    //return { init: function(){ addView.setDesk(desk).activate(); }};
    //return { init: function(){ editView.setTask(task).activate(); }};
});