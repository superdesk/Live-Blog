define([
    'backbone',
    'desk/views/member',
    'desk/views/add-members',
    'desk/views/edit-desk',

    'tmpl!superdesk-desk>config-desk'
], function(Backbone, MemberView, AddMembersView, EditDeskView) {
    return Backbone.View.extend({
        events: {
            'click .edit-members': 'editMembers',
            'click [data-click="delete"]': 'destroy',
            'click [data-click="edit"]': 'edit'
        },

        initialize: function() {
            this.model.users.on('reset', this.renderMembers, this);
            this.model.users.on('add', this.renderMembers, this);
            this.model.on('change', this.render, this);
        },

        render: function() {
            $(this.el).tmpl('superdesk-desk>config-desk', this.model.getView()).addClass('desk-config');
            this.fetchUsers();
            return this;
        },

        fetchUsers: function() {
            this.model.users.fetch({headers: this.model.users.xfilter, reset: true});
        },

        renderMembers: function() {
            var list = $(this.el).find('.user-list').empty();
            this.model.users.each(function(user) {
                var view = new MemberView({model: user});
                list.append(view.render().el);
            });
        },

        editMembers: function(e) {
            e.preventDefault();
            var view = new AddMembersView({model: this.model});
            $('#modal-placeholder').html(view.render().el);
            $(this.el).find('#addMember').modal('show');
        },

        destroy: function(e) {
            e.preventDefault();
            if (confirm(_("Are you sure you want to remove this desk?"))) {
                this.model.destroy();
                this.remove();
            }
        },

        edit: function(e) {
            e.preventDefault();
            var view = new EditDeskView({model: this.model});
            $('#modal-placeholder').html(view.render().el);
        }
    });
});
