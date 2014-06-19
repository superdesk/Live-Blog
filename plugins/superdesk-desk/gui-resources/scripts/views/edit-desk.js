define(['backbone', 'tmpl!superdesk-desk>edit-desk'], function(Backbone) {
    return Backbone.View.extend({
        events: {
            'click .save': 'save',
            'click .cancel': 'close',
            'submit form': 'save'
        },

        initialize: function() {
            if (!this.model) {
                this.model = new this.collection.model();
                this.model.url = this.collection.url;
            }
        },

        render: function() {
            $(this.el).tmpl('superdesk-desk>edit-desk', this.model.getView());
            $(this.el).find('.modal').modal('show');
            return this;
        },

        save: function(e) {
            e.preventDefault();

            var view = this;
            var data = {Name: $(this.el).find('#desk-name').val()};
            var isNew = this.model.isNew();
            this.model.save(data, {
                patch: !isNew,
                success: function(model) {
                    if (isNew) {
                        // workaround for missing x-filter fields on POST
                        model.fetch({
                            headers: view.collection.xfilter,
                            success: function(model) {
                                view.collection.add(model);
                            }
                        });
                    }
                    view.close(e);
                },
                error: function(model, response) {
                    var input = $(view.el).find('#desk-name').first();
                    input.closest('.control-group').addClass('error');
                }
            });
        },

        close: function(e) {
            e.preventDefault();
            var view = this;
            $(this.el).find('.modal').modal('hide', function() {
                view.remove();
            });
        }
    });
});
