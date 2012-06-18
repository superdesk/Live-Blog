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
            var type = Object.prototype.toString.call(arguments[i])
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
            var self = this;
            return { 
                read: function(cb, failCb, alwaysCb)
                { 
                    return $.ajax(source, Sync.options).done(cb).fail(failCb); 
                },
                update: function(data, cb, failCb, alwaysCb)
                {
                    data = typeof data == 'function' ? data.call(this) : data;
                }
            }
        },
        options: {dataType: 'json', type: 'get', headers: {'Accept' : 'text/json'}}
    };
        
    
    Model.prototype = 
    {
        changed: false,
        defaults: {},
        data: {},
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
        /*!
         * @param format
         */
        feed: function(format)
        {
            for( var i in this.data ) console.log(this.data[i])
            
        },
        /*!
         * data sync call
         */
        sync: function()
        { 
            var self = this;
            if( this.changed )
                return (this.href && this.dataAdapter(this.href).update(this.feed(), function()
                {
                    self.changed = false;
                })); 
            
            return (this.href && this.dataAdapter(this.href).read(function(data)
            {
                self.parse(data);
                $(self).trigger('update');
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
        hash: function(){ return this.href; }
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
        Model.prototype = proto;
        Model.prototype.pushUnique = function()
        {
            if( !uniqueList[this.hash()] ) uniqueList[this.hash()] = this;
            return uniqueList[this.hash()];
        };
        Model.prototype.getUniques = function()
        {
            return uniqueList;
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
            return (this.options.href && 
                this.dataAdapter(this.options.href).read(function(data)
                {
                    self.parse(data);
                    $(self).trigger('update');
                    $(self._list).trigger('update');
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
            this.total = data.total;
        }
    };
    
    return { Model: Model, Collection: Collection };
})


