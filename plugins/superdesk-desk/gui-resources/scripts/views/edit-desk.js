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
            }
        },

        render: function() {
            $(this.el).tmpl('superdesk-desk>edit-desk', this.model.getView());
            $(this.el).find('.modal').modal('show');
            return this;
        },

        save: function(e) {
            var data = {Name: $(this.el).find('#desk-name').val()};
            if (this.model.isNew()) {
                this.collection.create(data, {headers: {'X-Filter': 'Id'}, wait: true, sort: false});
            } else {
                this.model.save(data, {patch: true});
            }

            this.close(e);
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
