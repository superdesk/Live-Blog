define([
    'backbone',
    'gizmo/superdesk',
    'tmpl!superdesk-desk>config',
    'tmpl!superdesk-desk>config-desk'
], function(Backbone, Gizmo) {

    var Model = Backbone.Model.extend({
        idAttribute: 'Id'
    });

    var User = Model.extend({
    });

    var UserCollection = Backbone.Collection.extend({
        model: User
    });

    var Desk = Model.extend({
        parse: function(response) {
            this.users = new UserCollection({url: response.User.href});
            return response;
        }
    });

    var url = new Gizmo.Url('Desk/Desk');
    var DeskCollection = Backbone.Collection.extend({
        model: Desk,
        url: url.get(),

        parse: function(response) {
            return response.DeskList;
        }
    });

    var DeskView = Backbone.View.extend({
        render: function() {
            var data = {
                Name: this.model.get('Name')
            };

            $(this.el).tmpl('superdesk-desk>config-desk', data).addClass('desk-config');
            return this;
        }
    });

    var ConfigView = Backbone.View.extend({
        initialize: function() {
            this.collection.on('reset', this.render, this);
        },

        render: function() {
            $(this.el).tmpl('superdesk-desk>config', {});

            var list = $(this.el).find('.config-page-container').empty();
            this.collection.each(function(desk) {
                var view = new DeskView({model: desk});
                list.append(view.render().el);
            });

            return this;
        },

        fetchCollection: function() {
            this.collection.fetch({headers: {'X-Filter': 'Id, Name, User'}, reset: true});
        }
    });

    var desks = new DeskCollection();
    return new ConfigView({collection: desks});
});
