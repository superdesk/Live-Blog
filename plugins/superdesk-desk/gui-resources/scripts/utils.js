define(['gizmo/superdesk'], function(Gizmo) {
    return {
        getResourceUrl: function(resource) {
            var url = new Gizmo.Url(resource);
            return url.get();
        }
    };
});
