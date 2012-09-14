define(['gizmo', 'jquery', 'jquery/superdesk'], function(giz, $, superdesk)
{
    var AuthApp;
    // delete login on trigger logout from other apps
    require([config.lib_js_urn + 'views/auth'], function(a)
    {
        AuthApp = a;
        $(AuthApp).on('logout', function()
        {
            localStorage.removeItem('superdesk.login.session')
            delete authSync.options.headers.Authorization;
        });
    });
    
    var syncReset = function() // reset specific data and headers for superdesk
    {
        try
        { 
            delete this.options.headers['X-Filter'];
            delete this.options.data['CId.since'];
        }
        catch(e){}
    }, 
    newSync = $.extend({}, giz.Sync,
    {
        reset: syncReset
    }),
    
    // display auth view
    authLock = function()
    {
        var args = arguments,
            self = this;

            // reset headers on success
            AuthApp.success = function()
            { 
                self.options.headers.Authorization = localStorage.getItem('superdesk.login.session');
            };
            AuthApp.require.apply(self, arguments); 
    },
    
    authSync = $.extend({}, newSync, 
    {
        options: 
        { 
            // get login token from local storage
            headers: { 'Authorization': localStorage.getItem('superdesk.login.session') },
            // failuire function for non authenticated requests
            fail: function(resp)
            { 
                // TODO 404? shouldn't be covered by auth
                (resp.status == 404 || resp.status == 401) && authLock.apply(authSync, arguments); 
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
        this.syncAdapter.options.headers['X-Filter']
            = arguments.length > 1 ? $.makeArray(arguments).join(',') : $.isArray(arguments[0]) ? arguments[0].join(',') : arguments[0];
        return this;
    },
    since = function(val) // change id implementation
    {
        $.extend( this.syncAdapter.options, { data:{ 'CId.since': val }} );
    },
    asc = function(col)
    {
        $.extend( this.syncAdapter.options, { data:{ asc: col }} );
    },
    desc = function(col)
    {
        $.extend( this.syncAdapter.options, { data:{ desc: col }} );
    },
    Model = giz.Model.extend // superdesk Model 
    ({
        isDeleted: function(){ return this._forDelete || this.data.DeletedOn; },
        syncAdapter: newSync,
        xfilter: xfilter,
        since: since
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
    AuthModel = Model.extend // authenticated superdesk Model
    ({ 
        syncAdapter: authSync, xfilter: xfilter, since: since
    }),
    Collection = giz.Collection.extend
    ({
        xfilter: xfilter, since: since, asc: asc, desc: desc, syncAdapter: newSync
    }),
    AuthCollection = Collection.extend
    ({
        xfilter: xfilter, since: since, syncAdapter: authSync
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
		Register: giz.Register
    };
});