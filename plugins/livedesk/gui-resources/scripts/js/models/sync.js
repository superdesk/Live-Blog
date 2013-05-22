define(['backbone', 'gizmo/superdesk'], function(Backbone, Gizmo) {
    var url = new Gizmo.Url('LiveDesk/Sync');
    return Backbone.Model.extend({
        idAttribute: 'Id',
        urlRoot: url.get(),

        parse: function(response) {
            if (response && 'href' in response) {
                this.url = response.href;
                delete response.href;
            }

            if (response && 'Source' in response) {
                response.SourceId = response.Source.Id;
            }

            return response;
        }
    });
});
