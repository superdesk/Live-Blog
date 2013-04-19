define([
    'backbone',
    'desk/views/config-desk-user',
    'desk/views/add-members',

    'tmpl!superdesk-desk>config-desk'
], function(Backbone, UserView, AddMembersView) {
    return Backbone.View.extend({
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
            this.model.users.fetch({headers: this.model.users.xfilter, reset: true});
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
            var view = new AddMembersView({model: this.model});
            $('#modal-placeholder').html(view.render().el);
            $(this.el).find('#addMember').modal('show');
        }
    });
});
