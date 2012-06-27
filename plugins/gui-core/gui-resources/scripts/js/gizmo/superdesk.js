define(['gizmo', 'jquery/superdesk'], function(giz, superdesk)
{
    var newSync = $.extend({}, giz.Sync, 
    {
        options: { headers: { 'Authentication': 1 } },
        href: function(source)
        {
            return 'my/'+source;
        },
        reset: function()
        {
            try{ delete this.options.headers['X-Filter']; }catch(e){}
        }
    }),
    authModel = giz.Model.extend
    ({ 
        syncAdapter: newSync,
        xfilter: function()
        {
            if( this.syncAdapter.options.headers ) this.syncAdapter.options.headers = {};
            this.syncAdapter.options.headers['X-Filter']
                = arguments.length > 1 ? $.makeArray(arguments).join(',') : $.isArray(data) ? data.join(',') : data;
            return this;
        }
    });
    return {Model: giz.Model, AuthModel: authModel, Collection: giz.Collection, Sync: newSync}
});