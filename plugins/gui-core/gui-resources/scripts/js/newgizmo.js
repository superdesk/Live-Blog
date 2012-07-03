define(['jquery', 'jquery/utils', 'utils/extend', 'utils/class'], function()
{
	var Render = Class.extend({		
		getProperty: function(prop)
			{
				if (!this[prop]) return null;
				return (typeof this[prop] === 'function') ? this[prop]() : this[prop];
			}
	});
	/*Render.extend  =  function(prop){
		var newly;
		if(prop.render) {
			var propRender = prop.render;
			delete prop.render;	
			var newly = Class.extend.call(this, prop), protoRender = newly.prototype.render;
			newly.prototype.render = function(){
				if(protoRender !== undefined) {
					propRender.apply(this, arguments);
					return protoRender.apply(this, arguments);
				} else 
					return propRender.apply(this, arguments);
			}
		} else
			newly = Class.extend.call(this, prop);
		newly.extend = arguments.callee;	
		return newly;
	};*/
	var View = Render.extend({
		tagName: 'div',
		attributes: { className: '', id: ''},
		namespace: 'view',		
		_constructor: function(data, options)
		{
			$.extend(this, data);
			options = $.extend({}, { init: true, events: true, ensure: true}, options);
			options.ensure && this._ensureElement();
			options.init && this.init.apply(this, arguments);
			options.events && this.delegateEvents();
		},
		_ensureElement: function()
		{
			var className = this.attributes.className,
				id = this.attributes.id,
				el ='';
			if(!$(this.el).length) {
				if($.isString(this.el)) {
					if(this.el[0]=='.') {
						className = className + this.el.substr(0,1);
					} 
					if(this.el[0]=='#') {
						id = this.el.substr(0,1);
					}
				}
				el = '<'+this.tagName;
				if(className !== '') {
					el = el + ' class="'+className+'"';
				}
				if(id !== '') {
					el = el + ' id="'+id+'"';
				}
				el = el + '></'+this.tagName+'>';
				this.el = $(el);
			}
		},		
		init: function(){ return this; },
		resetEvents: function()
		{
			this.undelegateEvents();
			this.delegateEvents();
		},
		delegateEvents: function(events)
		{
			var self = this;
			if (!(events || (events = this.getProperty('events')))) return;
			for(var selector in events) {
				var one = events[selector];
				for(var evnt in one) {
					var other = one[evnt], sel = null, dat = {}, fn;
					if(typeof other === 'string') {
						fn  = other;
						if($.isFunction(self[fn])) {
							console.log(evnt + this.getNamespace(), selector, fn);
							console.log('it is: ',$(this.el));
							if(selector === "")
								$(this.el).on(evnt + this.getNamespace(), self[fn].bind(self));
							$(this.el).on(evnt + this.getNamespace(), selector, self[fn].bind(self));
						}
					}
				}
			}
		},
		getNamespace: function()
		{
			return '.'+this.getProperty('namespace');
		},
		undelegateEvents: function()
		{
			$(this.el).off(this.getNamespace());
		},
		render: function(){ 
			
			this.delegateEvents();
			return this; 
		},
		remove: function()
		{
			$(this.el).remove();
			return this;
		},
		setElement: function(el)
		{
			this.el = $(el);
			this._ensureElement();
		},
	});
    var Model = function(data)
    { 
        this._forDelete = false;
        this._changed = false;
        this.data = {};
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
            return this.data[key] === undefined? false : this.data[key];
        },
		toJSON: function()
		{
			return this.data;
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
            if( !this._clientHash ) this._clientHash = (new Date()).getTime();
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
        items: {}, counts: {}, instances: [], startCount: 10,
        /*!
         * 
         */
        get: function( obj, key )
        {
            this.counts[key] = this.counts[key] ? this.counts[key]+1 : this.startCount;
            return this.items[key];
        },
        /*!
         * 
         */
        set: function(key, val)
        {
            if( !this.items[key] ) this.items[key] = val;
            this.garbage();
            this.counts[key] = this.counts[key] ? this.counts[key]+1 : this.startCount;
            return this.items[key];
        },
        /*!
         * replace a key with another key value actually
         */
        replace: function(key, newKey, val)
        {
            delete this.items[key];
            delete this.counts[key];
            return this.set(newKey, val);
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
                    delete this.counts[key];
                }
            }
        },
        remove: function(key)
        {
            delete this.items[key];
            delete this.counts[key];
        }
    };
    // Model's base options
    var options = Model.options = {}, extendFnc;
    Model.extend = extendFnc = function(props, userProto)
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
        // extend with user defined proto
        userProto && $.extend(Model.prototype, userProto);
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
		toJSON: function(){
			var data=[];
			this.each(function(key, model){
				data[key] = model.toJSON();
			});
			return data;
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
		each: function(fn){
			$.each(this._list, fn);
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
		on: function(evt, fun, obj)
		{
			$(this).on(evt, function(evnt){
				fun.call(obj, evnt);
			});
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
            return model.sync(this.options.href);
        },
		save: function(model)
		{
            this.desynced = false;
            if( !(model instanceof Model) ) model = new this.model(model);
            return model.sync(model.href);		
		}
    };    
    return { Model: Model, Collection: Collection, View: View };
});