define(['gizmo/superdesk'], function(Gizmo) {
    var BlogProvider = Gizmo.Model.extend({});

    BlogProviderCollection = Gizmo.Collection.extend({
        model: BlogProvider,

        url: new Gizmo.Url('LiveDesk/BlogProvider'),

        init: function() {
            var collection = this;
            this.model.on('insert', function(model) {
                collection.trigger('add');
            });
        }
    });
});
