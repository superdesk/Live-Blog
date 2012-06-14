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
                }
            }
        },
        options: {dataType: 'json', type: 'get', headers: {'Accept' : 'text/json'}}
    };
        
    
    Model.prototype = 
    {
        defaults: {},
        _construct: function(data)
        {
            if( typeof data == 'string' ) this.href = data;
            if( typeof data == 'object' ) $.extend(this, data);
            return this.pushUnique();
        },
        dataAdapter: Sync.dataAdapter,
        sync: function()
        { 
            var self = this;
            return (this.href && 
                this.dataAdapter(this.href).read(function(data)
                {
                    self.parse(data);
                    $(self).trigger('update');
                })); 
        },
        parse: function(data)
        {
            for( var i in data ) 
            {
                if( this.defaults[i] &&  typeof this.defaults[i] === 'function' )
                {
                    this[i] = new this.defaults[i](data[i].href);
                    continue;
                }
                this[i] = data[i];
            }
        },
        hash: function(){ return this.href; }
    };
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


