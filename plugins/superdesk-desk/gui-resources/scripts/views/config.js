define([
    'backbone',
    'gizmo/superdesk',
    'tmpl!superdesk-desk>config',
    'tmpl!superdesk-desk>config-desk',
    'tmpl!superdesk-desk>add-desk',
    'tmpl!superdesk-desk>edit-members',
    'tmpl!superdesk-desk>select-user',
    'tmpl!superdesk-desk>list-user'
], function(Backbone, Gizmo) {

    var Model = Backbone.Model.extend({
        idAttribute: 'Id'
    });

    var userHeaders = {'X-Filter': 'Id, FullName, Name, EMail'};
    var User = Model.extend({
        getData: function() {
            return {
                name: this.getName(),
                email: this.get('EMail'),
                id: this.id,
                selected: this.get('selected')
            };
        },

        getName: function() {
            if (this.get('FullName')) {
                return this.get('FullName');
            } else {
                return this.get('Name');
            }
        },

        getResource: function() {
            return {
                Id: this.id,
                FullName: this.get('FullName'),
                Name: this.get('Name'),
                EMail: this.get('Email')
            };
        }
    });

    var url = new Gizmo.Url('HR/User');
    var UserCollection = Backbone.Collection.extend({
        model: User,
        url: url.get(),

        parse: function(response) {
            return response.UserList;
        },

        comparator: function(user) {
            return user.getName().toLowerCase();
        }
    });

    var deskHeaders = {'X-Filter': 'Id, Name, User'};

    var Desk = Model.extend({
        parse: function(response) {
            this.users = new UserCollection([], {url: response.User.href});
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

    var UserView = Backbone.View.extend({
        tagName: 'li',

        initialize: function() {
            this.model.on('destroy', this.remove, this);
        },

        render: function() {
            $(this.el).tmpl('superdesk-desk>list-user', this.model.getData());
            return this;
        }
    });

    var SelectUserView = Backbone.View.extend({
        tagName: 'li',

        events: {
            'change input:checkbox': 'toggle'
        },

        render: function() {
            $(this.el).tmpl('superdesk-desk>select-user', this.model.getData());
            return this;
        },

        toggle: function() {
            this.model.set('selected', !this.model.get('selected'));
        }
    });

    var EditMembersView = Backbone.View.extend({
        events: {
            'click .save': 'save',
            'click .cancel': 'close',
            'change .toggle-all': 'toggleAll'
        },

        initialize: function() {
            this.users = new UserCollection();
            this.users.on('reset', this.renderUsers, this);
        },

        render: function() {
            $(this.el).tmpl('superdesk-desk>edit-members');
            this.users.fetch({reset: true, headers: userHeaders});
            return this;
        },

        renderUsers: function() {
            var selected = this.collection;
            var list = $(this.el).find('.internal-collaborators').empty();
            this.users.each(function(user) {
                if (selected.findWhere({'Id': user.id})) {
                    user.set('selected', true);
                }

                var view = new SelectUserView({model: user});
                list.append(view.render().el);
            });
        },

        save: function(e) {
            var selected = new UserCollection(this.users.where({'selected': true}));
            var members = this.collection;

            console.log('selected', selected.pluck('Id'));
            console.log('members', members.pluck('Id'));

            members.each(function(user) {
                if (!selected.findWhere({Id: user.id})) {
                    user.destroy({wait: true});
                }
            });

            selected.each(function(user) {
                members.create(user.getResource());
            });

            this.close(e);
        },

        close: function(e) {
            e.preventDefault();
            $(this.el).find('#addMember').modal('hide', function() {
                view.remove();
            });
        }
    });

    var DeskView = Backbone.View.extend({
        events: {
            'click .edit-members': 'editMembers'
        },

        initialize: function() {
            this.model.users.on('reset', this.renderMembers, this);
            this.model.users.on('add', this.renderMembers, this);
        },

        render: function() {
            var data = {
                Name: this.model.get('Name')
            };

            $(this.el).tmpl('superdesk-desk>config-desk', data).addClass('desk-config');

            this.fetchUsers();
            return this;
        },

        fetchUsers: function() {
            this.model.users.fetch({headers: userHeaders, reset: true});
        },

        renderMembers: function() {
            var list = $(this.el).find('.user-list').empty();
            this.model.users.each(function(user) {
                var view = new UserView({model: user});
                list.append(view.render().el);
            });
        },

        editMembers: function(e) {
            e.preventDefault();
            var view = new EditMembersView({collection: this.model.users});
            $('#modal-placeholder').html(view.render().el);
            $(this.el).find('#addMember').modal('show');
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
            $('#modal-placeholder').html(view.render().el);
        }
    });

    var desks = new DeskCollection();
    return new ConfigView({collection: desks});
});
