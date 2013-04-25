define(['jquery', 'backbone', 'tmpl!livedesk>manage-feeds-edit'], function($, Backbone) {
    return Backbone.View.extend({
        events: {
            'click #edit-provider-save': 'save',
            'click #edit-provider-cancel': 'close',
            'click .close': 'close',
            'submit form': 'save'
        },

        initialize: function() {
            if (!this.model) {
                this.model = new this.collection.model();
            }
        },

        render: function() {
            $(this.el).tmpl('livedesk>manage-feeds-edit', this.model.render());
            this.modal = $(this.el).find('.modal');
            this.modal.modal('show');
            return this;
        },

        save: function(e) {
            e.preventDefault();
            var data = {
                Name: $(this.el).find('#edit-provider-title').val(),
                URI: $(this.el).find('#edit-provider-url').val()
            };

            if (this.model.isNew()) {
                this.collection.create(data, {headers: this.collection.xfilter, wait: true});
            } else {
                this.model.save(data, {patch: true});
            }

            return this.close(e);
        },

        close: function(e) {
            e.preventDefault();
            var view = this;
            this.modal.modal('hide', function() { view.remove(); });
        }
    });
});
