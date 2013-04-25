define([
    'backbone',
    'desk/views/select-user',

    'tmpl!superdesk-desk>edit-members'
], function(Backbone, SelectUserView) {
    return Backbone.View.extend({
        events: {
            'click .save': 'save',
            'click .cancel': 'close',
            'change .toggle-all': 'toggleAll',
            'change input[name="search"]': 'search',
            'blur input[name="search"]': 'search'
        },

        initialize: function() {
            this.users = this.model.unassignedUsers;
            this.users.on('reset', this.renderUsers, this);
            this.users.on('change', this.updateToggle, this);
            this.usersUrl = this.users.url;
        },

        render: function() {
            $(this.el).tmpl('superdesk-desk>edit-members');
            this.fetchUsers();
            return this;
        },

        fetchUsers: function() {
            this.users.fetch({reset: true, headers: this.users.xfilter});
        },

        renderUsers: function() {
            var list = $(this.el).find('.internal-collaborators').empty();
            this.users.each(function(user) {
                var view = new SelectUserView({model: user});
                list.append(view.render().el);
            });
        },

        save: function(e) {
            var selected = new Backbone.Collection(this.users.where({'selected': true}));
            var members = this.model.users;

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
        },

        toggleAll: function(e) {
            var checked = $(e.target).prop('checked');
            this.users.each(function(user) {
                user.set('selected', checked);
            });
        },

        updateToggle: function() {
            var checkbox = $(this.el).find('.toggle-all');
            checkbox.prop('checked', this.users.length == this.users.where({'selected': true}).length);
        },

        search: function(e) {
            var query = $(e.target).val();

            if (query.length) {
                this.users.url = this.usersUrl + '?name=' + query;
            } else {
                this.users.url = this.usersUrl;
            }

            this.fetchUsers();
        }
    });
});
