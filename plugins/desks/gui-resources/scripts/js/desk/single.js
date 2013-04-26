define
([
    'jquery',
    'backbone',
    'gizmo/superdesk',
    'gizmo/superdesk/action',
    config.guiJs('superdesk/desks', 'models/desk'),
    config.guiJs('superdesk/desks', 'models/task'),
    config.guiJs('superdesk/desks', 'models/task-status'),
    'tmpl!superdesk/desks>desk/single',
    'tmpl!superdesk/desks>desk/task',
    'tmpl!superdesk/desks>desk/desk-select',
    'tmpl!superdesk/desks>desk/desk-select-option',
    'tmpl!superdesk/desks>desk/status'
],
function($, Backbone, Gizmo, Action, Router)
{
    var optionsStatus = {headers: {'X-Filter': 'Key'}, reset: true};
    var optionsTask = {headers: {'X-Filter': 'Id, Description, Title, StartDate, Status.Key'}, reset: true};
    var optionsDesk = {headers: {'X-Filter': 'Id, Description, Name'}, reset: true};

    /**
     * Get gizmo url for given path
     *
     * @param {string} path
     * @return {string}
     */
    function getGizmoUrl(path)
    {
        var url = new Gizmo.Url(path);
        return url.get();
    }

    /**
     * Get id from given url
     *
     * @param {string} url
     * @return {string}
     */
    function parseId(url)
    {
        return url.split('/').slice(-1)[0];
    }

    /**
     * Desk Model
     */
    var 
    Base = Backbone.Model.extend({
        idAttribute: 'Id',
        parse: function(response) {
            if (!response) {
                return;
            }

            if ('href' in response) {
                this.url = response.href;
                delete response.href;
                this.id = parseId(this.url);
            }
            if(this.parseData)
                this.parseData(response);
            else
                return response;
        }
    }),
    Desk = Base.extend({
        idAttribute: 'Id',
        defaults: {
            Description: 'some text',
            Name: 'Desk'
        }
    }),
    
    Task = Base.extend({
        defaults: {
            Description: 'some text',
            Title: 'some title',
            StartDate: (new Date()).toISOString(),
            Status: {'Key':'Miau'}
        }
    }),
    
    Status = Base.extend({
        idAttribute: 'Key'
    }),
    DeskCollection = Backbone.Collection.extend({
        model: Desk,
        parse: function(response) {
            return response.DeskList;
        }
    }),
    DeskSelectOptionView = Backbone.View.extend({
        tagName: 'li',
        render: function(){
            var self = this;
            this.$el.tmpl('superdesk/desks>desk/desk-select-option', this.model.toJSON(), function() {
                //self.$el.append(o);
            });
            return this;
        }
    }),
    SelectDeskCollectionView = Backbone.View.extend({
        attributes: {
            'class': "btn-group pull-left"
        },
        render: function() {
            var self = this;
            this.$el.tmpl('superdesk/desks>desk/desk-select', {}, function() {
                deskCollection.url = getGizmoUrl('Desk/Desk');
                deskCollection.fetch(optionsDesk).done(function(){
                    deskCollection.each(function(option) {
                        var dso = new DeskSelectOptionView({model: option});
                        self.$el.find('.sf-dropdown').append(dso.render().el);
                    })
                })
            });
            return this;
        }
    }),
    StatusCollection = Backbone.Collection.extend({
        model: Status,
        parse: function(response) {
            return response.TaskStatusList;
        }
    }),
    TaskCollection = Backbone.Collection.extend({
        model: Task,
        parse: function(response) {
            return response.TaskList;
        },
        byStatus: function(status) {
            filtered = this.filter(function(task) {
              return task.get('Status').Key == status;
            });
            return filtered;
        }
    }),


    TaskView = Backbone.View.extend({
        tagName: 'li',
        init: function() {
            //this.render();
        },
        render: function() {
            var self = this;
            $.tmpl('superdesk/desks>desk/task', this.model.toJSON(), function(e, o) {
                self.$el.append(o)
            });
            return this;
        }
    }),
    StatusesView = Backbone.View.extend({
        initialize: function(attrs) {
            this.options = attrs;
            this.listenTo(this.collection,'reset', this.render);
        },
        render: function() {
            var self = this;
            self.$el.html('');
            taskCollection = new TaskCollection;
            taskCollection.url = getGizmoUrl('Desk/Desk/' + this.options.deskId + '/Task');
            taskCollection.fetch(optionsTask).done(function(){      
                self.collection.each(function(status){
                    self.addOne(status, taskCollection);
                });
            });
        },
        addOne: function(status, taskCollection) {
            var statusKey = status.get('Key');
            var containerClass = statusKey.replace(' ', '') + '-container';
            status.set('containerClass', containerClass);
            var self = this;
            $.tmpl('superdesk/desks>desk/status', status.toJSON(), function(e, o) {
                self.$el.append(o);
                var fCollection = taskCollection.byStatus(statusKey);
                for ( var i = 0; i < fCollection.length; i ++) {
                    var task = fCollection[ i ];
                    var taskView = new TaskView({model:task});
                    var tviewel = taskView.render().el;
                    self.$el.find('.' + containerClass + ' .assignments').append(tviewel);
                }
            });
        }
    }),
    MainView = Backbone.View.extend({
        events: {
            
            'click .select-desk': 'selectDesk',
            'click #compact-view': 'toggleCompactView',
            'click #grid-view': 'setGridView',
            'click #list-view': 'setListView'
        },
        toggleCompactView: function(evt) {
            console.log('compact view');
            var target = $(evt.target);
            console.log(target);
            if (target.hasClass('active')) {
                console.log('has');
                $("#main-desk").removeClass('compact-desk');
            }
            else {
                console.log('has not');
                $("#main-desk").addClass('compact-desk');
            }
        },
        selectDesk:function(evt) {
            var self = this;
            var deskId = $(evt.target).attr('data-id');
            var deskName = $(evt.target).attr('data-name');
            self.$el.find('#selected-desk').html(deskName);
            statusCollection = new StatusCollection;
            statusCollection.url = getGizmoUrl('Desk/TaskStatus');
            statusCollection.fetch(optionsStatus);

            new StatusesView({
                el: $('#statuses-list'),
                collection: statusCollection,
                deskId: deskId
            });
        },
        setGridView: function(evt) {
            if (!$('#li-grid-view').hasClass('active')) {
                $('#li-grid-view').addClass('active');
                $("#li-list-view").removeClass('active');
                $(".desk-content-container").removeClass('desk-list');
            }
            return false;
        },
        setListView: function(evt) {
            if (!$('#li-list-view').hasClass('active')) {
                $('#li-list-view').addClass('active');
                $("#grid-view").parent().removeClass('active');
                $(".desk-content-container").addClass('desk-list');
            }
            return false;
        },
        render: function(deskId) {
            var self = this;
            this.$el.tmpl('superdesk/desks>desk/single', {}, function() {

                var deskSelect = new SelectDeskCollectionView;
                self.$el.find('#desk-select').html(deskSelect.render().el);
                
            });
        }
    }),
   
    deskCollection = new DeskCollection;

    return {
        init: function() {
            var mainView = new MainView( { el: $('#area-main')} );
            mainView.render();
        }
    }
});