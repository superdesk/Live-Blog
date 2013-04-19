define
([
    'jquery',
    'backbone',
    'gizmo/superdesk',
    'gizmo/superdesk/action',
    config.guiJs('superdesk/desks', 'router'),
    config.guiJs('superdesk/desks', 'models/desk'),
    config.guiJs('superdesk/desks', 'models/task'),
    config.guiJs('superdesk/desks', 'models/task-status'),
    'tmpl!superdesk/desks>desk/single'
],
function($, Backbone, Gizmo, Action, Router)
{
    var optionsStatus = {headers: {'X-Filter': 'Key, IsOn'}, reset: true},
        router = new Router;

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
        defaults: {
            Description: 'some text',
            Name: 'Desk'
        },
        parseData: function(response) {
            if ('Id' in response) {
                return {
                    'Id': response.Id,
                    'Name': response.Name,
                    'Description': response.Description
                };
            }
        }
    }),
    
    Task = Base.extend({
        defaults: {
            Description: 'some text',
            Title: 'some title',
            StartDate: (new Date()).toISOString()
        }
    }),
    
    Status = Base.extend({
        idAttribute: 'Key'
    });

    StatusCollection = Backbone.Collection.extend({
        model: Status,
        parse: function(response) {
            return response.TaskStatusList;
        }
    }),
    MainView = Backbone.View.extend({
        render: function() {
            var self = this;
            $(this.el).tmpl('superdesk/desks>desk/single',{}, function(){
                new StatusesView({
                    el: self.$el.find('.single-desk'),
                    collection: statusCollection
                });
                
                router.navigate('//desks/task/edit');
            });
        }
    }),

    StatusesView = Backbone.View.extend({
        initialize: function() {
            this.listenTo(this.collection,'reset', this.render);
        },
        render: function() {
            this.collection.each(function(status){
                console.log(status.toJSON());
            });
        }
    }),

    statusCollection = new StatusCollection;


    return {
        init: function(){
            console.log('hey');
            var mainView = new MainView({ el: $('#area-main')});
            mainView.render();
            statusCollection.url = getGizmoUrl('Desk/TaskStatus');
            statusCollection.fetch(optionsStatus);
        }
    }
});