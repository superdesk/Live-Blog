define([
    'backbone',
    'gizmo/superdesk',
    'tmpl!superdesk-desk>config',
    'tmpl!superdesk-desk>config-desk',
    'tmpl!superdesk-desk>add-desk'
], function(Backbone, Gizmo) {

    var Model = Backbone.Model.extend({
        idAttribute: 'Id'
    });

    var User = Model.extend({
    });

    var UserCollection = Backbone.Collection.extend({
        model: User
    });

    var deskHeaders = {'X-Filter': 'Id, Name, User'};

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

    var AddDeskView = Backbone.View.extend({
        events: {
            'click .save': 'save',
            'click .cancel': 'close'
        },

        render: function() {
            $(this.el).tmpl('superdesk-desk>add-desk');
            return this;
        },

        save: function(e) {
            var data = {
                'Name': $(this.el).find('#desk-name').val()
            };

            this.collection.create(data, {headers: deskHeaders});
            this.close(e);
        },

        close: function(e) {
            e.preventDefault();
            var view = this;
            $(this.el).find('#addDesk').modal('hide', function() {
                view.remove();
            });
        }
    });

    var ConfigView = Backbone.View.extend({
        events: {
            'click #add-desk': 'addDesk'
        },

        initialize: function() {
            this.collection.on('reset', this.render, this);
            this.collection.on('add', this.render, this);
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
            this.collection.fetch({headers: deskHeaders, reset: true});
        },

        addDesk: function(e) {
            e.preventDefault();
            var view = new AddDeskView({collection: this.collection});
            $(this.el).find('#modal-placeholder').html(view.render().el);
        }
    });

    var desks = new DeskCollection();
    return new ConfigView({collection: desks});
});
