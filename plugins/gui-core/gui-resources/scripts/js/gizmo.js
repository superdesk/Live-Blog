define('gizmo', ['jquery', 'utils/class'], function($,Class)
{
    var Register = function(){},
	Model = function(data){},
    Uniq = function()
    { 
        this.items = {}; 
        //$(this.instances).trigger('garbage');
        //this.instances.push(this);
    },
    Collection = function(){},
	Url = Class.extend({
		_constructor: function(arg) {		
			this.data = { root: ''};
			switch( $.type(arg) )
			{
				case 'string':
					this.data.url = arg; 
					break;
				case 'array': 
					this.data.url = arg[0];
					if(arg[1] !== undefined) this.data.xfilter = url[0];
					break;
				case 'object': // options, same technique as above
					this.data.url = arg.url
					if(arg.xfilter !== undefined) this.data.xfilter = arg.xfilter;
					break;
			}			
			return this;
		},
		xfilter: function() {
			this.data.xfilter = arguments.length > 1 ? $.makeArray(arguments).join(',') : $.isArray(arguments[0]) ? arguments[0].join(',') : arguments[0];		
			return this;
		},
		root: function(root) {
			this.data.root = root;
			return this;
		},
		get: function(){
			return this.data.root + this.data.url;
		},
		order: function(key, direction) {
			this.data.order = direction+'='+key;
			return this;
		},
		filter: function(key, value) {
			this.data.filter = key+'='+value;
			return this;
		},
		
		options: function() {
			
			var options = {};
			if(this.data.xfilter)
				options.headers = { 'X-Filter': this.data.xfilter};
			return options;
		}
	}),    
    Sync = 
    {
        request: function(source)
        {
            var self = this,
                reqFnc = function(data, predefinedOptions, userOptions)
                {
					if(source instanceof Url) {
						var options = $.extend(true, {}, predefinedOptions, self.options, userOptions, {data: data}, source.options());
						self.reset();
						//console.log('Source: ',source.get());
						return $.ajax(self.href(source.get()), options);
					} else {				
						var options = $.extend(true, {}, predefinedOptions, self.options, userOptions, {data: data});
						self.reset();
						return $.ajax(self.href(source), options);
					}
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
            this._forDelete = false;
            this._changed = false;
            this.data = {};
            this.changeset = {};
            this._clientHash = null;
            if( typeof data == 'string' ) this.href = data;
            if( typeof data == 'object' ) $.extend(this.data, this.parse(data));
            if( options && typeof options == 'object' ) $.extend(this, options);
         
            //this.exTime = new Date
            //this.exTime.setMinutes(this.exTime.getMinutes() + 5);
            
            var newInstance = this.pushUnique ? this.pushUnique() : this; 
            
            // identify changes from new data
            // TODO optimize
            if( typeof data == 'object' ) 
            {
                var changes = {}, changed = false;
                for( var i in data ) 
                    if( !newInstance.data[i] || (data[i] != newInstance.data[i] && typeof data[i] != 'object') )
                    {
                        newInstance.data[i] = changes[i] = data[i];
                        changed = true;
                    }
                changed && newInstance.triggerHandler('update', [changes]);
            }
            
            return newInstance;
        },
        /*!
         * adapter for data sync
         */
        syncAdapter: Sync,
        /*!
         * @param format
         */
        feed: function(format, deep, fromData)
        {
            var ret = {},
                feedData = fromData ? fromData : this.data;
            for( var i in feedData ) 
                ret[i] = feedData[i] instanceof Model ? 
                        (deep ? feedData[i].feed(deep) : feedData[i].relationHash() || feedData[i].hash()) : 
                        feedData[i];
            return ret;
        },
        /*!
         * data sync call
         */
        sync: function()
        {   
            var self = this, ret, dataAdapter = function(){ return self.syncAdapter.request.apply(self.syncAdapter, arguments); };
            this.hash();
            // trigger an event before sync
            self.triggerHandler('sync');
            
            if( this._forDelete ) // handle delete
                return dataAdapter(arguments[0] || this.href).remove().done(function()
                { 
                    self.triggerHandler('delete');
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
                    self.triggerHandler('insert')
						.class.triggerHandler('insert', self);
                });
            }
            
            if( this._changed ) // if changed do an update on the server and return
                ret = (this.href && dataAdapter(this.href)
                        .update(arguments[1] ? this.feed() : this.feed('json', false, this.changeset))
                        .done(function()
                {
                    self._changed = false;
                    self.changeset = {};
                    self.triggerHandler('update');
                })); 
            else
                // simply read data from server
                ret = (this.href && dataAdapter(this.href).read(arguments[0]).done(function(data)
                {
                    self.parse(data);
                    self.triggerHandler('read');
                }));
            
            return ret;
        },
        remove: function()
        {
            this._forDelete = true;
            return this;
        },
        isDeleted: function()
        {
            return this._forDelete;  
        },
        /*!
         * @param data the data to parse into the model
         * @param updateChangeset whether to update changeset or not
         */
        parse: function(data, updateChangeset)
        {
            for( var i in data ) 
            {
                if( this.defaults[i] ) switch(true)
                {
                    case typeof this.defaults[i] === 'function': // a model or collection constructor
                        
                        var newModel = new this.defaults[i](data[i]);
                        
                        if( updateChangeset && newModel != this.data[i])
                            this.changeset[i] = newModel;

                        this.data[i] = newModel;
                        !data[i].href && this.data[i].relationHash && this.data[i].relationHash(data[i]);
                        continue;
                        break;
                    case $.isArray(this.defaults[i]): // a collection
                        delete this.data[i];
                        this.data[i] = new Collection(this.defaults[i][0], data[i].href); 
                        continue;
                        break;
                    case this.defaults[i] instanceof Collection: // an instance of some colelction/model
                    case this.defaults[i] instanceof Model:
                        this.data[i] = this.defaults[i];
                        continue;
                        break;
                }
                if( updateChangeset && this.data[i] != data[i] ) this.changeset[i] = data[i];
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
            this.parse(data, true);
            this._changed = true;
            return this;
        },
        /*!
         * used for new models not yet saved on the api
         */
        _getClientHash: function()
        {
            //console.log('client hash', this._getClientHash());
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
        relationHash: function(val){ if(val) this.data.Id = val; return this.data.Id; },
		/*!
		 * used to place events on this model, 
		 * scope of the call method is sent as obj argument
		 */
		on: function(evt, handler, obj)
		{
			if(obj === undefined)
				$(this).on(evt, handler);
			else
				$(this).on(evt, function(){
					handler.call(obj, evt);
				});
			return this;
		},
        /*!
         * used to trigger model events
		 * this also calls the model method with the event name
         */
		trigger: function(evt, data)
		{
			$(this).trigger(evt, data);
			return this;
		},
        /*!
         * used to trigger handle of model events
		 * this doens't call any method see: trigger
         */
		triggerHandler: function(evt, data)
		{
			$(this).triggerHandler(evt, data);
			return this;
		}
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
    var options = Model.options = {}, extendFnc, cextendFnc;
    Model.extend = extendFnc = function(props, options)
    {
        var newly;
        newly = Class.extend.call(this, props);
        newly.extend = extendFnc;
        newly.prototype.class = newly;
        newly.on = function(event, handler, obj)
        {
            $(newly).on(event, function(){ handler.apply(obj, arguments); }); 
        };
        newly.triggerHandler = function(event, data){ $(newly).triggerHandler(event, data); };
		
        if(options && options.register) {
			Register[options.register] = newly;
			delete options.register;
		}
        // create a new property from original options one
        newly.prototype.options = $.extend({}, options);

		return newly;
    };
    
    Collection.prototype = 
    {
        _list: [],
        getList: function(){ return this._list; },
        count: function(){ return this._list.length; },
        _construct: function()
        {
            if( !this.model ) this.model = Model;
            this._list = [];
            this.desynced = true;
            var buildData = buildOptions = function(){ void(0); },
                self = this;
            for( var i in arguments ) 
            {
                switch( $.type(arguments[i]) )
                {
                    case 'function': // a model
                        this.model = arguments[i]; 
                        break;
                    case 'string': // a data source
                        this.href = arguments[i]; 
                        break;
                    case 'array': // a list of models, a function we're going to call after setting options
                        buildData = (function(args){ return function(){ this._list = this.parse(args); }})(arguments[i]); 
                        break;
                    case 'object': // options, same technique as above
						//console.log(arguments[i], arguments[i] instanceof Url);
                        buildOptions = (function(args){ return function(){ this.options = args; }})(arguments[i]);
                        break;
                }
            }
            // callbacks in order
            buildOptions.call(this);
            buildData.call(this);
        },
        get: function(key)
        {
            var dfd = $.Deferred(),
                self = this;
                searchKey = function()
                {
                    for( var i=0; i<self._list.length; i++ )
                        if( key == self._list[i].hash() || key == self._list[i].relationHash() ) 
                            return dfd.resolve(self._list[i]);
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
            this.href = href;
            return this;
        },
		each: function(fn){
			$.each(this._list, fn);
		},		
        feed: function(format, deep)
        {
            var ret = [];
            for( var i in this._list ) 
                ret[i] = this._list[i].feed(format, deep);
            return ret;
        },		
        /*!
         * @param options 
         */
        sync: function()
        {
            var self = this;
            return (this.href &&
                this.syncAdapter.request.call(this.syncAdapter, this.href).read(arguments[0]).done(function(data)
                {
                    var data = self.parse(data);
                     // important or it will infiloop
                    for( var i=0; i < data.list.length; i++ )
                    {
                        var model = false;
                        for( var j=0; j<self._list.length; j++ )
                            if( data.list[i].hash() == self._list[j].hash() )
                            {
                                model = data.list[i];
                                break;
                            }
                        
                        if( !model ) self._list.push(data.list[i]);
                        else if( model.isDeleted() ) self._list[i].remove();
                    }
                    self.desynced = false;
                    $(self._list).on('delete', function(){ self.remove(this.hash()); });
                    $(self._list).on('garbage', function(){ this.desynced = true; });
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
            list = [];
            for( var i in theData )
                list.push( new this.model(theData[i]) );
            return {list: list, total: data.total};
        },
        insert: function(model)
        {
            this.desynced = false;
            if( !(model instanceof Model) ) model = new this.model(model);
            this._list.push(model);
            model.hash();
            var x = model.sync(this.options.href);
            return x;
        },
		/*!
		 * used to place events on this model, 
		 * scope of the call method is sent as obj argument
		 */
		on: function(evt, handler, obj)
		{
			if( obj === undefined )
				$(this).on(evt, handler);
			else
				$(this).on(evt, function(){ handler.call(obj, evt); });
			return this;
		},	
        /*!
         * used to trigger model events
		 * this also calls the model method with the event name
         */
		trigger: function(evt)
		{
			$(this).trigger(evt);
			return this;
		},
        /*!
         * used to trigger handle of model events
		 * this doens't call any method see: trigger
         */
		triggerHandler: function(evt)
		{
			$(this).triggerHandler(evt);
			return this;
		}        
    };
    
    Collection.extend = cextendFnc = function(props)
    {
        var newly;
        newly = Class.extend.call(this, props);
        newly.extend = cextendFnc;
        if(options && options.register)
			Collection[options.register] = newly;		
        return newly;
    };
    /*{
        var proto = new this;
        $.extend(proto, props);
        for( var name in props ) proto[name] = props[name];
        
        function Collection()
        {
            if( this._construct ) return this._construct.apply(this, arguments);
        };
        Collection.prototype = proto;
        // create a new property from original options one
        Collection.prototype.options = $.extend({}, options);
        Collection.prototype.constructor = Collection;
        Collection.extend = cextendFnc;
        return Collection;
    };*/
    
    // view
    
    var Render = Class.extend
    ({     
        getProperty: function(prop)
        {
            if (!this[prop]) return null;
            return (typeof this[prop] === 'function') ? this[prop]() : this[prop];
        }
    }),
    View = Render.extend
    ({
        tagName: 'div',
        attributes: { className: '', id: ''},
        namespace: 'view',      
        _constructor: function(data, options)
        {
            $.extend(this, data);
            options = $.extend({}, { init: true, events: true, ensure: true}, options);
            options.ensure && this._ensureElement();
            options.init && this.init.apply(this, arguments);
            console.log('init delegate');
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
							$(this.el).on(this.getEvent(evnt), selector, self[fn].bind(self));
                        }
                    }
                }
            }
        },
		getEvent: function(evnt){
			return evnt + this.getNamespace();
		},
        getNamespace: function()
        {
            return '.'+this.getProperty('namespace');
        },
        undelegateEvents: function()
        {
            $(this.el).off(this.getProperty('namespace'));
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
            console.log('Set element');
			this.el = $(el);
            this._ensureElement();
			this.delegateEvents();
        }
    });
    
    return { Model: Model, Collection: Collection, Sync: Sync, UniqueContainer: Uniq, View: View, Url: Url, Register: Register};
});
