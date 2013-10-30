define(['vendor/backbone'], function(Backbone) {

    // Override Backbone.sync to use the PUT HTTP method for PATCH requests
    // when doing Model#save({...}, { patch: true });
    // from https://github.com/documentcloud/backbone/issues/2152#issuecomment-12356051
    var originalSync = Backbone.sync;
    Backbone.sync = function(method, model, options) {
        if (method === 'patch') options.type = 'PUT';
        return originalSync(method, model, options);
    };

    return Backbone;
});
