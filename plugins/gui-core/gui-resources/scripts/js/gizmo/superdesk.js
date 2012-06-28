define(['gizmo', 'jquery', 'jquery/superdesk'], function(giz, $, superdesk)
{
    var Model = giz.Model.extend({}),
    
    newSync = $.extend({}, giz.Sync, 
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
    
    Model.extend = function()
    {
        var Model = giz.Model.extend.apply(this, arguments);
        
        var uniq = new giz.UniqueContainer;
        $.extend( Model.prototype, { _uniq: uniq, pushUnique: function(){ return uniq.set(this.hash(), this); } }, arguments[0] );
        return Model;
    };
    
    return { Model: Model, AuthModel: authModel, Collection: giz.Collection, Sync: newSync };
});