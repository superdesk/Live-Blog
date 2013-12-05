define(['gizmo', 'jquery', 'jquery/superdesk'], function(giz, $, superdesk)
{
    var AuthApp, ErrorApp;
    // delete login on trigger logout from other apps
    require([config.cjs('views/auth.js')], function(a)
    {
        AuthApp = a;
        $(AuthApp).on('logout', function()
        {
            localStorage.removeItem('superdesk.login.session')
            delete authSync.options.headers.Authorization;
        });
    });
    // error display
    require([config.lib_js_urn + 'views/error'], function(a)
    {
        ErrorApp = a;
    });
    
    var syncReset = function() // reset specific data and headers for superdesk
    {
        try
        { 
            delete this.options.headers['X-Filter'];
            this.options.data = {};
        }
        catch(e){}
    }, 
    newSync = $.extend({}, giz.Sync,
    {
        reset: syncReset
    }),
    
    authSync = $.extend({}, newSync, 
    {
        options: 
        { 
            // get login token from local storage
            headers: { 'Authorization': localStorage.getItem('superdesk.login.session') },
            // failure function for erroneous requests
            fail: function(resp)
            { 
                (resp.status == 401) && AuthApp.renderPopup(_('Please login to continue!')); 
                (resp.status == 404) && ErrorApp.require.apply(this, arguments);
            } 
        },
        href: function(source)
        {
            if($.type(source) === 'object') {
                /* @TODO: fix this wierd behaviour of the Gizmo.Url
                 *    get method isn't returnig the source.data instead the previous one
                 * this only happens for Actions url where the extend is done with jquery extend.
                 */ 
                //console.log('Source: ',source.data);
                //source = source.get();
                //console.log('Source: ',source);
                //source = source.data.root+source.data.url;
                source = source.getUrl();
            }
            //var ret = source.indexOf('my/') === -1 ? source.replace('resources/','resources/my/') : source;
            var ret = source;
            return ret;
        }
    }),
    xfilter = function() // x-filter implementation
    {
        if( !this.syncAdapter.options.headers ) this.syncAdapter.options.headers = {};
        this.syncAdapter.options.headers['X-Filter']
            = arguments.length > 1 ? $.makeArray(arguments).join(',') : $.isArray(arguments[0]) ? arguments[0].join(',') : arguments[0];
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
    Model = giz.Model.extend // superdesk Model 
    ({
        isDeleted: function(){ return this._forDelete || this.data.DeletedOn; },
        syncAdapter: newSync,
        xfilter: xfilter
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
    Config = function(key, value) {
        if( value === undefined) {
            return this._config[key];
        } else {
            this._config[key] = value;
        }
    },
    _config = {
        limit: 15
    },
    AuthModel = Model.extend // authenticated superdesk Model
    ({ 
        syncAdapter: authSync, xfilter: xfilter
    }),
    Collection = giz.Collection.extend
    ({
        xfilter: xfilter, param: param, since: since, until: until, start: start, end: end, asc: asc, desc: desc, limit: limit, offset: offset, _config: _config, config: Config, syncAdapter: newSync
    }),
    AuthCollection = Collection.extend
    ({
        xfilter: xfilter, param: param, since: since, until: until, start: start, end: end, asc: asc, desc: desc, limit: limit, offset: offset, _config: _config, config: Config, syncAdapter: authSync
    }),
    
 // set url helper property with superdesk path
    Url = giz.Url.extend
    ({      
        _construct: function()
        {
            this.data = !this.data ? { root: superdesk.apiUrl+'/resources/'} : this.data;
            giz.Url.prototype._construct.apply(this, arguments);
        }
    })
    ;
    
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
        Auth: Auth,
        Model: Model, AuthModel: AuthModel, 
        Collection: Collection, AuthCollection: AuthCollection, 
        Sync: newSync, AuthSync: authSync,
		View: giz.View,
		Url: Url,
		Register: giz.Register,
		Superdesk: {}
    };
});