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

            var data = this.getData();

            try {
                if (this.model.isNew()) {
                    this.collection.create(data, {headers: this.collection.xfilter, wait: true});
                } else {
                    this.model.save(data, {patch: true, wait: true});
                }

                return this.close(e);
            } catch (errors) {
                this.renderErrors(errors);
            }
        },

        close: function(e) {
            e.preventDefault();
            var view = this;
            this.modal.modal('hide', function() { view.remove(); });
        },

        getData: function() {
            var data = {};

            $(this.el).find('input[data-field]').each(function() {
                data[$(this).attr('data-field')] = $(this).val();
            });

            return data;
        },

        renderErrors: function(errors) {
            $(this.el).find('input[data-field]').each(function() {
                var $input = $(this);
                if (errors.indexOf($input.attr('data-field')) !== -1) {
                    $input.closest('.control-group').addClass('error');
                    $input.next('span').show();
                } else {
                    $input.closest('.control-group').removeClass('error');
                    $input.next('span').hide();
                }
            });
        }
    });
});
