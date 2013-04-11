define(['jquery', 'backbone', 'tmpl!livedesk>manage-feeds-edit'], function($, Backbone) {
    /**
     * Edit provider view
     */
    return Backbone.View.extend({
        events: {
            'click #edit-provider-save': 'save',
            'click #edit-provider-cancel': 'close',
            'click .close': 'close'
        },

        initialize: function() {
            this.render(); // render on init
        },

        render: function() {
            $(this.el).tmpl('livedesk>manage-feeds-edit');
            this.title = $(this.el).find('#edit-provider-title');
            this.url = $(this.el).find('#edit-provider-url');
            this.modal = $(this.el).find('.modal');

            if (this.model) {
                this.title.val(this.model.get('Name'));
                this.url.val(this.model.get('URI'));
                $(this.el).find('h3').text(_('Edit Provider ' + this.model.get('Name')));
            } else {
                $(this.el).find('h3').text(_('Add Provider'));
            }

            this.options.target.append(this.el);
            this.modal.modal('show');
            return this;
        },

        save: function() {
            var data = {
                Name: this.title.val(),
                URI: this.url.val()
            };

            if (!this.model) {
                this.collection.create(data);
            } else {
                this.model.save(data);
            }

            return this.close();
        },

        close: function() {
            this.modal.modal('hide');
            this.remove();
            return false;
        }
    });
});
