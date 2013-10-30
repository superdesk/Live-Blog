define([ 'gizmo/superdesk', 'jquery', 'gizmo/superdesk/models/actions' ], 
function( gizmo, $, Actions )
{
    var newActions = new Actions();
    gizmo.Superdesk.action =
    {
        actions: newActions,
        cache: {},
        /*!
         * 
         */
        clearCache: function()
        {
            this.cache = {};
            this.actions._list = [];
        },
        /*!
         * @param string path 
         * @returns $.Deferred()
         */
        getMore: function(path, url)
        {
            var dfd = new $.Deferred,
                self = this,

                searchCache = function()
                {
                    var results = [], searchPath = path; 
                    //if( path.lastIndexOf('*') === path.length-1 ) searchPath = path.substr(0, path.length-1);
                    searchPath = searchPath.split('*').join('%').replace(/([.?*+^$[\]\\(){}|-])/g, "\\$1").replace(/%/g,'[\\w\\d\\-_]+');
                    searchPath = new RegExp(searchPath+'$');
                    for( var i in self.cache ) // match path plz
                        if( self.cache[i].get('Path').search(searchPath) === 0 )
                            results.push(self.cache[i]);
                    return results;    
                },
                cachedResults = searchCache();
                
            if( cachedResults.length === 0 )
            {
                self.actions
                    .sync({data: {path: path}})
                    .done(function()
                    { 
                        self.actions.each(function(){ self.cache[this.get('Path')] = this; });
                        dfd.resolve(searchCache());
                    })
                    .fail(function(){ dfd.reject(); });
                return dfd;
            }
            return dfd.resolve(cachedResults);
        },
        
        /*!
         * get one action from a path
         */
        get: function(path, url)
        {
            var dfd = new $.Deferred,
                self = this;
            if( !self.cache[path] )
            {
                var searchPath = path.substr(0, path.lastIndexOf('.'));
                self.actions.sync({data: {path: searchPath+'.*'}})
                    .done(function()
                    { 
                        self.actions.each(function(){ self.cache[this.get('Path')] = this; });
                        self.cache[path] && dfd.resolve(self.cache[path]);
                        dfd.reject();
                    })
                    .fail(function(){ dfd.reject(); });
                return dfd;
            }
            return dfd.resolve(self.cache[path]);
        },
           
        /*!
         * get a bunch of scripts from a path and initialize them
         * @param string path
         */
        initApps: function(path)
        {
            var args = []; 
            Array.prototype.push.apply( args, arguments );
            args.shift();
            return this.getMore(path).done(function(apps) {
                for (var i = 0; i < apps.length; i++) {
                    var action = apps[i];
                    apps[i].get('Script') && require([apps[i].get('Script').href], function(app) {
                        args.push(action);
                        app && app.init && app.init.apply(app, args);
                        args.pop();
                    });
                }
            });
        },
        initApp: function(path)
        {
            var args = []; 
            Array.prototype.push.apply( args, arguments );
            args.shift();
            return this.get(path).done(function( app )
            { 
                app.get('Script') && require([app.get('Script').href], function(app)
                {
                    app && app.init && app.init.apply( app, args );
                }); 
            });
        }
           
    };
    
    return gizmo.Superdesk.action;
});
