define(['gizmo', 'jquery', 'jquery/superdesk'], function(giz, $, superdesk)
{
    var syncReset = function() // reset specific data and headers for superdesk
    {
        try
        { 
            delete this.options.headers['X-Filter'];
            delete this.options.data['startEx.CId'];
        }
        catch(e){}
    }, 
    newSync = $.extend({}, giz.Sync,
    {
        reset: syncReset
    }),
    authSync = $.extend({}, newSync, 
    {
        options: { headers: { 'Authorization': localStorage.getItem('superdesk.login.session') } },
        href: function(source)
        {
            return source.indexOf('my/') === -1 ? source.replace('resources/','resources/my/') : source;
        }
    }),
    xfilter = function() // x-filter implementation
    {
        if( !this.syncAdapter.options.headers ) this.syncAdapter.options.headers = {};
        this.syncAdapter.options.headers['X-Filter']
            = arguments.length > 1 ? $.makeArray(arguments).join(',') : $.isArray(arguments[0]) ? arguments[0].join(',') : arguments[0];
        return this;
    },
    since = function(val) // change id implementation
    {
        $.extend( this.options, { data:{ 'startEx.CId': val }} );
    },
    asc = function(col)
    {
        $.extend( this.options, { data:{ asc: col }} );
    },
    desc = function(col)
    {
        $.extend( this.options, { data:{ desc: col }} );
    },
    Model = giz.Model.extend // superdesk Model 
    ({
        isDeleted: function(){ return this._forDelete && this.data.DeletedOn; },
        syncAdapter: newSync,
        xfilter: xfilter,
        since: since
    }),
    AuthModel = Model.extend // authenticated superdesk Model
    ({ 
        syncAdapter: authSync, xfilter: xfilter, since: since
    }),
    Collection = giz.Collection.extend
    ({
        xfilter: xfilter, since: since, syncAdapter: newSync
    }),
    AuthCollection = Collection.extend
    ({
        xfilter: xfilter, since: since, syncAdapter: authSync
    });
    
    // finally add unique container model
    Model.extend = function()
    {
        var Model = giz.Model.extend.apply(this, arguments);
        
        var uniq = new giz.UniqueContainer;
        $.extend( Model.prototype, 
        { 
            _uniq: uniq, 
            pushUnique: function()
            { 
                return uniq.set(this.hash(), this); 
            } 
        }, arguments[0] );
        return Model;
    };
    
    return { 
        Model: Model, AuthModel: AuthModel, 
        Collection: Collection, AuthCollection: AuthCollection, 
        Sync: newSync, AuthSync: authSync,
		View: giz.View,
		Url: giz.Url,
		Register: giz.Register		
    };
});