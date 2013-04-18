define([
    'backbone',
    'desk/views/edit-desk',
    'desk/views/config-desk',
    'desk/models/desk-collection',

    'tmpl!superdesk-desk>config'
], function(Backbone, EditDeskView, DeskView, DeskCollection) {
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
            this.collection.fetch({headers: this.collection.xfilter, reset: true});
        },

        addDesk: function(e) {
            e.preventDefault();
            var view = new EditDeskView({collection: this.collection});
            $('#modal-placeholder').html(view.render().el);
        }
    });

    var desks = new DeskCollection();
    return new ConfigView({collection: desks});
});
