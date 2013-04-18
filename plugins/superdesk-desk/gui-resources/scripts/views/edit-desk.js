define(['backbone', 'tmpl!superdesk-desk>edit-desk'], function(Backbone) {
    return Backbone.View.extend({
        events: {
            'click .save': 'save',
            'click .cancel': 'close'
        },

        render: function() {
            $(this.el).tmpl('superdesk-desk>edit-desk');
            return this;
        },

        save: function(e) {
            var data = {Name: $(this.el).find('#desk-name').val()};
            this.collection.create(data, {headers: this.collection.xfilter, wait: true});
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
});
