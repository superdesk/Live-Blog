define('gizmo', ['jquery'], function()
{
    var Model = function(data){ return false; },
    Collection = function()
    {
        this.model = Model;
        this._list = [];
        this.options = {};
        
        var buildData = buildOptions = function(){ void(0); },
            self = this;
            
        for( var i in arguments ) 
        {
            if( typeof arguments[i] === 'function')
            {
                this.model = arguments[i];
                continue;
            }
            var type = Object.prototype.toString.call(arguments[i]);
            if( type == '[object Array]' )
                buildData = (function(args){ return function(){ this._list = this.parse(args); }})(arguments[i]);
            if( type == '[object Object]' )
                buildOptions = (function(args){ return function(){ this.options = args; }})(arguments[i]);
        }
        buildOptions.call(this);
        buildData.call(this);
    };
    
    Sync = 
    {
        dataAdapter: function(source)
        {
            var reset = function()
            {
                Sync.options = {}; 
            };
            return { 
                read: function(cb, failCb, alwaysCb)
                { 
                    var options = $.extend({}, Sync.readOptions, Sync.options);
                    reset();
                    return $.ajax(source, options).done(cb).fail(failCb); 
                },
                update: function(data, cb, failCb, alwaysCb)
                {
                    var options = $.extend({}, Sync.updateOptions, Sync.options, {data: data});
                    reset();
                    return $.ajax(source, options).done(cb).fail(failCb);
                }
            }
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
            $.extend( Sync.options, {
                headers: {
                    'X-Filter': arguments.length > 1 ? $.makeArray(arguments).join(',') : $.isArray(data) ? data.join(',') : data
            }});
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
            var self = this;
            
            if( this.changed ) // if changed do an update on the server and return
                return (this.href && this.dataAdapter(this.href).update(this.feed(), function()
                {
                    self.changed = false;
                    $(self).triggerHandler('update');
                })); 
            
            // simply read data from server
            return (this.href && this.dataAdapter(this.href).read(function(data)
            {
                self.parse(data);
                $(self).triggerHandler('read');
            }));  
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
        hash: function(){ return this.data[this.hashKey]; },
        /*!
         * used to relate models. a general standard key would suffice
         */
        relationHash: function(){ return this.data.Id; }
    };
    
    var Uniq = function(){};
    Uniq.prototype = 
    {
        items: {},
        counts: {},
        get: function( obj, key )
        {
            if( this.items[key] ) delete obj;
            else this.items[key] = obj;
            this.counts[key]++;
            return this.items[key];
        },
        set: function(key, val)
        {
            if( !this.items[key] ) this.items[key] = val;
            this.counts[key]++;
            this.garbage();
            return this.items[key];
        },
        garbage: function()
        {
            for( var key in this.counts ) 
            {
                this.counts[key]--;
                if( this.counts[key] == 0 )
                {
                    $(this.items[key]).trigger('garbage');
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
        var uniqueList = {};
        var uniq = new Uniq;
        Model.prototype = proto;
        Model.prototype.pushUnique = function()
        {
            return uniq.set(this.hash(), this);
            //if( !uniqueList[this.hash()] ) uniqueList[this.hash()] = this;
            //return uniqueList[this.hash()];
        };
        Model.prototype.getUniques = function()
        {
            return uniq;
        };
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
            for( var i in this._list ) if( key == this._list[i].hash() ) return this._list[i];
            return undefined;
        },
        dataAdapter: Sync.dataAdapter,
        sync: function()
        {
            var self = this;
            return (this.options.href && !this.synced &&
                this.dataAdapter(this.options.href).read(function(data)
                {
                    self.parse(data);
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
            theData = extracListData(data);
            for( var i in theData ) 
                this._list.push( new this.options.model(theData[i]) );
            
            $(this._list).on('garbage', function(){ this.synced = false; })
            this.total = data.total;
        }
    };
    
    return { Model: Model, Collection: Collection };
})


