define('gizmo', ['jquery'], function()
{
    var Model = function(data)
    { 
        
    },
    Uniq = function()
    { 
        this.items = {}; 
        this.counts = {};
        $(this.instances).trigger('garbage');
        this.instances.push(this);
    },
    Collection = function()
    {
        this.model = Model;
        this._list = [];
        this.options = {};
        this.desynced = true;
        
        var buildData = buildOptions = function(){ void(0); },
            self = this;
            
        for( var i in arguments ) 
        {
            switch( Object.prototype.toString.call(arguments[i]) )
            {
                case '[object Function]': // a model
                    this.model = arguments[i]; 
                    break;
                case '[object String]': // a data source
                    this.options.href = arguments[i]; 
                    break;
                case '[object Array]': // a list of models, a function we're going to call after setting options
                    buildData = (function(args){ return function(){ this._list = this.parse(args); }})(arguments[i]); 
                    break;
                case '[object Object]': // options, same technique as above
                    buildOptions = (function(args){ return function(){ this.options = args; }})(arguments[i]);
                    break;
            }
        }
        // callbacks in order
        buildOptions.call(this);
        buildData.call(this);
    };
    
    Sync = 
    {
        dataAdapter: function(source)
        {
            return { 
                read: function(userOptions)
                { 
                    var options = $.extend({}, Sync.readOptions, Sync.options, userOptions);
                    return $.ajax(source, options); 
                },
                update: function(data, userOptions)
                {
                    var options = $.extend({}, Sync.updateOptions, Sync.options, userOptions, {data: data});
                    return $.ajax(source, options);
                }
            };
        },
        options: {},
        readOptions: {dataType: 'json', type: 'get', headers: {'Accept' : 'text/json'}},
        updateOptions: {type: 'post', headers: {'X-HTTP-Method-Override': 'PUT'}},
        insertOptions: {type: 'post'},
        deleteOptions: {type: 'post', headers: {'X-HTTP-Method-Override': 'DELETE'}}
    };
        
    
    Model.prototype = 
    {
        changed: false,
        defaults: {},
        data: {},
        hashKey: 'href',
        /*!
         * constructor
         */ 
        _construct: function(data, options)
        {
            this.changed = false;
            this.data = {}; 
            this._xfilter = null;
            if( typeof data == 'string' ) this.href = data;
            if( typeof data == 'object' ) $.extend(this.data, data);
            if( options && typeof options == 'object' ) $.extend(this.options, data);
            return this.pushUnique();
        },
        /*!
         * adapter for data sync
         */
        dataAdapter: Sync.dataAdapter,
        xfilter: function(data)
        {
            this._xfilter = {headers: {'X-Filter': arguments.length > 1 ? $.makeArray(arguments).join(',') : $.isArray(data) ? data.join(',') : data}};
            return this;
        },
        /*!
         * @param format
         */
        feed: function(format)
        {
            var ret = {};
            for( var i in this.data ) 
                ret[i] = this.data[i] instanceof Model ? this.data[i].relationHash() : this.data[i];
            return ret;
        },
        /*!
         * data sync call
         */
        sync: function()
        { 
            var self = this, ret;
            
            if( this.changed ) // if changed do an update on the server and return
                ret = (this.href && this.dataAdapter(this.href).update(this.feed(), this._xfilter).done(function()
                {
                    self.changed = false;
                    $(self).triggerHandler('update');
                })); 
            
            // simply read data from server
            ret = (this.href && this.dataAdapter(this.href).read(this._xfilter).done(function(data)
            {
                self.parse(data);
                $(self).triggerHandler('read');
            }));  
            this._xfilter = null;
            return ret;
        },
        /*!
         * @param data the data to parse into the model
         */
        parse: function(data)
        {
            for( var i in data ) 
            {
                if( this.defaults[i] &&  typeof this.defaults[i] === 'function' )
                {
                    this.data[i] = new this.defaults[i](data[i].href);
                    continue;
                }
                if(this.defaults[i] && $.isArray(this.defaults[i]))
                {
                    delete this.data[i];
                    this.data[i] = new Collection(this.defaults[i][0], data[i].href); 
                    continue;
                }
                this.data[i] = data[i];
            }
        },
        get: function(key)
        {
            return this.data[key];
        },
        set: function(key, val)
        {
            var data = {}; data[key] = val;
            this.parse(data);
            this.changed = true;
            return this;
        },
        /*!
         * represents the formula to identify the model uniquely
         */
        hash: function(){ return this.data[this.hashKey] || this.href; },
        /*!
         * used to relate models. a general standard key would suffice
         */
        relationHash: function(){ return this.data.Id; }
    };
    
    Uniq.prototype = 
    {
        items: {}, counts: {}, instances: [],
        /*!
         * 
         */
        get: function( obj, key )
        {
            this.counts[key] = this.counts[key] ? this.counts[key]+1 : 10;
            return this.items[key];
        },
        /*!
         * 
         */
        set: function(key, val)
        {
            if( !this.items[key] ) this.items[key] = val;
            this.garbage();
            this.counts[key] = this.counts[key] ? this.counts[key]+1 : 10;
            return this.items[key];
        },
        /*!
         * 
         */
        garbage: function()
        {
            for( var key in this.counts ) 
            {
                this.counts[key]--;
                if( this.counts[key] == 0 )
                {
                    $(this.items[key]).triggerHandler('garbage');
                    delete this.items[key];
                }
            }
        }
    };
    // Model's base options
    var options = Model.options = {};
    Model.extend = function(props)
    {
        var proto = new this;
        for( var name in props ) proto[name] = props[name];
        
        function Model()
        {
            if( this._construct ) return this._construct.apply(this, arguments);
        };
        var uniq = new Uniq;
        Model.prototype = proto;
        Model.prototype.pushUnique = function()
        {
            return uniq.set(this.hash(), this);
        };
        Model.prototype._uniq = uniq;
        // create a new property from original options one
        Model.prototype.options = $.extend({}, options);
        Model.prototype.constructor = Model;
        return Model;
    };
    
    Collection.prototype = 
    {
        _list: [],
        get: function(key)
        {
            var dfd = $.Deferred(),
                self = this;
                searchKey = function()
                {
                    for( var i in self._list )
                        if( key == self._list[i].hash() || key == self._list[i].relationHash() ) 
                            return dfd.resolve(self._list[i]);
                };
            this.desynced && this.sync().done(function(){ dfd.resolve(searchKey()); }) ? dfd : searchKey();
            return dfd;
        },
        dataAdapter: Sync.dataAdapter,
        setHref: function(href)
        {
            this.options.href = href;
            return this;
        },
        sync: function()
        {
            var self = this;
            return (this.options.href &&
                this.dataAdapter(this.options.href).read(/*HARDCODE*/,{headers: {'X-Filter': 'Id'}}).done(function(data)
                {
                    self.parse(data);
                    self.desynced = false;
                    $(self).triggerHandler('read');
                    $(self._list).triggerHandler('read');
                }));
        },
        parse: function(data)
        {
            // get the important list data from request
            var extractListData = function(data)
            {
                var ret = data;
                if( !Array.isArray(data) ) for( i in data ) 
                {
                    if( $.isArray(data[i]) )
                    {
                        ret = data[i];
                        break;
                    }
                }
                return ret;
            },
            theData = extractListData(data);
            for( var i in theData ) 
                this._list.push( new this.model(theData[i]) );
            $(this._list).on('garbage', function(){ this.desynced = true; })
            this.total = data.total;
        }
    };
    
    return { Model: Model, Collection: Collection };
})
