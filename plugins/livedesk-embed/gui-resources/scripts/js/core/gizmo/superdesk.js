define([ 'jquery', 'gizmo' ], function( $, Gizmo)
{
    var syncReset = function() // reset specific data and headers for superdesk
    {
        try
        { 
            delete this.options.headers['X-Filter'];
            this.options.data = {};
        }
        catch(e){}
    }, 
    newSync = $.extend({}, Gizmo.Sync,
    {
        reset: syncReset
    }),
    
    authSync = $.extend({}, newSync, 
    {
        options: 
        {
			
            // get login token from local storage
			//console.log('why');
            //headers: { 'Authorization': localStorage.getItem('superdesk.login.session') },
            // failuire function for non authenticated requests
            fail: function(resp)
            { 
                // TODO 404? shouldn't be covered by auth
                (resp.status == 401) && authLock.apply(authSync, arguments);
                (resp.status == 404) && ErrorApp.require.apply(this, arguments);
            } 
        },
        href: function(source)
        {
            return source.indexOf('my/') === -1 ? source.replace('resources/','resources/my/') : source;
        }
    }),
    xfilter = function() // x-filter implementation
    {
        if( !this.syncAdapter.options.headers ) this.syncAdapter.options.headers = {};
        this._xfilter = arguments.length > 1 ? $.makeArray(arguments).join(',') : $.isArray(arguments[0]) ? arguments[0].join(',') : arguments[0];
		this.syncAdapter.options.headers['X-Filter'] = this._xfilter;
		this.syncAdapter.options.headers['X-Format-DateTime'] = "yyyy-MM-ddTHH:mm:ss'Z'";
        return this;
    },
    param = function(value, key)
	{
        if(value === undefined)
			delete this.syncAdapter.options.data[key];
		else {
			if(this.syncAdapter.options.data === undefined)
				this.syncAdapter.options.data = {};
			this.syncAdapter.options.data[key] = value;
		}
		return this;
	},
	since = function(value, key) // change id implementation
    {
		if(key === undefined)
			key = 'CId';
		return param.call(this, value, key+'.since');
    },
	until = function(value, key) // change id implementation
    {
		if(key === undefined)
			key = 'CId';
		return param.call(this, value, key+'.until');
    },	
	start = function(value, key) // change id implementation
    {
		if(key === undefined)
			key = 'CId';
		return param.call(this, value, key+'.start');
    },	
	end = function(value, key) // change id implementation
    {
        if(key === undefined)
			key = 'CId';
		return param.call(this, value, key+'.end');
    },	

    asc = function(value)
    {
		return param.call(this, value, 'asc');
    },
    desc = function(value)
    {
		return param.call(this, value, 'desc');
    },
	limit = function(value)
	{
        return param.call(this, value, 'limit');
	},
	offset = function(value)
	{
		return param.call(this, value, 'offset');
	},
    Model = Gizmo.Model.extend // superdesk Model 
    ({
        isDeleted: function(){ return this._forDelete || this.data.DeletedOn; },
        syncAdapter: newSync,
        xfilter: xfilter,
        since: since,
		until: until,
		start: start,
		end: end
    }),
    Auth = function(model)
    {
        if( typeof model === 'object' )
            model.syncAdapter = authSync; 
        model.modelDataBuild = function(model)
        {
            return Auth(model);
        };
        return model;
    },
    AuthModel = Gizmo.Model.extend // authenticated superdesk Model
    ({ 
        syncAdapter: authSync, xfilter: xfilter, since: since, until: until
    }),
    Collection = Gizmo.Collection.extend({
        xfilter: xfilter, since: since, until: until, start: start, end: end, asc: asc, desc: desc, limit: limit, offset: offset, syncAdapter: newSync
    }),
    AuthCollection = Gizmo.Collection.extend
    ({
        xfilter: xfilter, since: since, until: until, start: start, end: end, syncAdapter: authSync
    }),
 // set url helper property with superdesk path
    Url = Gizmo.Url.extend
    ({      
        _construct: function()
        {
            this.data = !this.data ? { 
                root: (liveblog.restServer? liveblog.restServer : liveblog.frontendServer)+'/resources/'} : this.data;
            Gizmo.Url.prototype._construct.apply(this, arguments);
        }
    });

    // finally add unique container model
    Model.extend = function()
    {
        var Model = Gizmo.Model.extend.apply(this, arguments);
        
        var uniq = new Gizmo.UniqueContainer;
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
        Auth: Auth,
        Model: Model, AuthModel: AuthModel, 
        Collection: Collection, AuthCollection: AuthCollection, 
        Sync: newSync, AuthSync: authSync,
		View: Gizmo.View,
		Url: Url,
		Register: Gizmo.Register
    };
});