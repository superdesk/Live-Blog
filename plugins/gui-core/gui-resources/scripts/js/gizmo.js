define('gizmo', ['jquery'], function()
{
    var Model = function(data)
    { 
        this._forDelete = false;
        this._changed = false;
        this.data = {};
    },
    Uniq = function()
    { 
        this.items = {}; 
        //$(this.instances).trigger('garbage');
        //this.instances.push(this);
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
        request: function(source)
        {
            var self = this,
                reqFnc = function(data, predefinedOptions, userOptions)
                {
                    var options = $.extend(true, {}, predefinedOptions, self.options, userOptions, {data: data});
                    self.reset();
                    return $.ajax(self.href(source), options);
                };
                
            return { 
                
                read: function(userOptions){ return reqFnc({}, self.readOptions, userOptions); },
                
                update: function(data, userOptions){ return reqFnc(data, self.updateOptions, userOptions); },
                
                insert: function(data, userOptions){ return reqFnc(data, self.insertOptions, userOptions); },
                
                remove: function(userOptions){ return reqFnc({}, self.removeOptions, userOptions); }
            };
        },
        href: function(source){ return source; },
        reset: $.noop,
        // bunch of options for each type of operation 
        options: {},
        readOptions: {dataType: 'json', type: 'get', headers: {'Accept' : 'text/json'}},
        updateOptions: {type: 'post', headers: {'X-HTTP-Method-Override': 'PUT'}},
        insertOptions: {dataType: 'json', type: 'post'},
        removeOptions: {type: 'get', headers: {'X-HTTP-Method-Override': 'DELETE'}}
    };
        
    var uniqueIdCounter = 0;
    Model.prototype = 
    {
        _changed: false,
        defaults: {},
        data: {},
        /*!
         * constructor
         */ 
        _construct: function(data, options)
        {
            this._changed = false;
            this.data = {}; 
            this._clientHash = null;
            if( typeof data == 'string' ) this.href = data;
            if( typeof data == 'object' ) $.extend(this.data, data);
            if( options && typeof options == 'object' ) $.extend(this, options);
         
            //this.exTime = new Date
            //this.exTime.setMinutes(this.exTime.getMinutes() + 5);
            
            return this.pushUnique ? this.pushUnique() : this;
        },
        /*!
         * adapter for data sync
         */
        syncAdapter: Sync,
        /*!
         * @param format
         */
        feed: function(format)
        {
            var ret = {};
            for( var i in this.data ) 
                ret[i] = this.data[i] instanceof Model ? this.data[i].relationHash() || this.data[i].hash() : this.data[i];
            return ret;
        },
        /*!
         * data sync call
         */
        sync: function()
        {    
            var self = this, ret, dataAdapter = function(){ return self.syncAdapter.request.apply(self.syncAdapter, arguments); };
            
            // trigger an event before sync
            $(self).triggerHandler('sync');
            
            if( this._forDelete ) // handle delete
                return dataAdapter(arguments[0] || this.href).remove().done(function()
                { 
                    $(self).triggerHandler('delete');
                    self._uniq && self._uniq.remove(self.hash());
                });
            
            if( this._clientHash ) // handle insert
            {
                var href = arguments[0] || this.href;
                return dataAdapter(href).insert(this.feed()).done(function(data)
                {
                    self._changed = false;
                    self.parse(data);
                    self._uniq && self._uniq.replace(self._clientHash, self.hash(), self);
                    self._clientHash = null;
                    $(self).triggerHandler('insert');
                }); 
            }
            
            if( this._changed ) // if changed do an update on the server and return
                ret = (this.href && dataAdapter(this.href).update(this.feed()).done(function()
                {
                    self._changed = false;
                    $(self).triggerHandler('update');
                })); 
            else
                // simply read data from server
                ret = (this.href && dataAdapter(this.href).read().done(function(data)
                {
                    self.parse(data);
                    $(self).triggerHandler('read');
                }));
            
            return ret;
        },
        remove: function()
        {
            this._forDelete = true;
            return this;
        },
        /*!
         * @param data the data to parse into the model
         */
        parse: function(data)
        {
            for( var i in data ) 
            {
                if( this.defaults[i] )
                    switch(true)
                    {
                        case typeof this.defaults[i] === 'function': // a model
                            this.data[i] = new this.defaults[i](data[i].href);
                            !data[i].href && this.data[i].relationHash(data[i]);
                            continue;
                            break;
                        case $.isArray(this.defaults[i]): // a collection
                            delete this.data[i];
                            this.data[i] = new Collection(this.defaults[i][0], data[i].href); 
                            continue;
                            break;
                        case this.defaults[i] instanceof Collection: // an already defined collection
                            this.data[i] = this.defaults[i];
                            continue;
                            break;
                    }
                this.data[i] = data[i];
            }
        },
        get: function(key)
        {
            $(this).triggerHandler('get-prop');
            return this.data[key];
        },
        set: function(key, val)
        {
            var data = {}; 
            if( val ) data[key] = val;
            else data = key;
            this.parse(data);
            this._changed = true;
            return this;
        },
        /*!
         * used for new models not yet saved on the api
         */
        _getClientHash: function()
        {
            if( !this._clientHash ) this._clientHash = "mcid-"+String(uniqueIdCounter++);
            return this._clientHash;
        },
        /*!
         * represents the formula to identify the model uniquely
         */
        hash: function()
        {
            if( !this.href && this.data.href ) this.href = this.data.href;
            return this.data.href || this.href || this._getClientHash(); 
        },
        /*!
         * used to relate models. a general standard key would suffice
         */
        relationHash: function(val){ if(val) this.data.Id = val; return this.data.Id; }
    };
    
    /*!
     * defs for unique storage of models
     */
    Uniq.prototype = 
    {
        items: {}, 
        garbageTime: 1500, //300000,
        refresh: function(val)
        {
            if( !val._exTime ) val._exTime = new Date;
            val._exTime.setTime(val._exTime.getTime() + this.garbageTime); 
        },
        /*!
         * 
         */
        set: function(key, val)
        {
            var self = this;
            $(val).on('sync get get-prop set-prop', function(){ self.refresh(this); });
            self.refresh(val);
            if( !this.items[key] ) this.items[key] = val;
            return this.items[key];
        },
        /*!
         * replace a key with another key value actually
         */
        replace: function(key, newKey, val)
        {
            delete this.items[key];
            return this.set(newKey, val);
        },
        /*!
         * 
         */
        garbage: function()
        {
            //console.log('running garbage on '+Object.keys(this.items).length+' items');
            for( var key in this.items ) 
            {
                if( this.items[key]._exTime && this.items[key]._exTime < new Date ) 
                {
                    //console.log('removing model: '+key);
                    $(this.items[key]).triggerHandler('garbage');
                    delete this.items[key];
                }    
            }
        },
        remove: function(key)
        {
            delete this.items[key];
        }
    };
    // Model's base options
    var options = Model.options = {}, 
    extendFnc = function(props)
    {
        var proto = new this;
//            uniq = new Uniq;
//        proto.pushUnique = function()
//        {
//            return uniq.set(this.hash(), this);
//        };
//        proto._uniq = uniq;
        $.extend(proto, props);
        for( var name in props ) proto[name] = props[name];
        
        function Model()
        {
            if( this._construct ) return this._construct.apply(this, arguments);
        };
        Model.prototype = proto;
        // create a new property from original options one
        Model.prototype.options = $.extend({}, options);
        Model.prototype.constructor = Model;
        Model.extend = extendFnc;
        return Model;
    };
    
    Collection.prototype = 
    {
        _list: [],
        getList: function(){ return this._list },
        get: function(key)
        {
            var dfd = $.Deferred(),
                self = this;
                searchKey = function()
                {
                    for( var i in self._list )
                    {
                        //console.log( key, self._list[i], key == self._list[i].hash(), key == self._list[i].relationHash() )
                        if( key == self._list[i].hash() || key == self._list[i].relationHash() ) 
                            return dfd.resolve(self._list[i]);
                    }
                    dfd.reject();
                };
            this.desynced && this.sync().done(function(){ dfd.resolve(searchKey()); }) ? dfd : searchKey();
            return dfd;
        },
        remove: function(key)
        {
            for( var i in this._list )
                if( key == this._list[i].hash() || key == this._list[i].relationHash() )
                {
                    Array.prototype.splice.call(this._list, i, 1);
                    break;
                }
            return this;
        },
        syncAdapter: Sync,
        /*!
         * 
         */
        setHref: function(href)
        {
            this.options.href = href;
            return this;
        },
        /*!
         * 
         */
        sync: function()
        {
            var self = this;
            return (this.options.href &&
                this.syncAdapter.request.call(this.syncAdapter, this.options.href).read(/*HARDCODE*/{headers: {'X-Filter': 'Id'}}).done(function(data)
                {
                    self.parse(data);

                    $(self._list).on('delete', function(){ self.remove(this.hash()); });
                    $(this._list).on('garbage', function(){ this.desynced = true; });

                    self.desynced = false;
                    $(self).triggerHandler('read');
                    $(self._list).triggerHandler('read');
                }));
        },
        /*!
         * 
         */
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
            this._list = [];
            for( var i in theData )
                this._list.push( new this.model(theData[i]) );
            
            this.total = data.total;
        },
        insert: function(model)
        {
            this.desynced = false;
            if( !(model instanceof Model) ) model = new this.model(model);
            this._list.push(model);
            return model.sync(this.options.href);
        }
    };
    
    Model.extend = Collection.extend = extendFnc;
    
    return { Model: Model, Collection: Collection, Sync: Sync, UniqueContainer: Uniq };
});
