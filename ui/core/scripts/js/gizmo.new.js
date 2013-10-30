define('gizmo', ['jquery', 'utils/class'], function($,Class)
{
    function compareObj(x, y)
    {
      var p;
	  if( (typeof(x)=='undefined') || (typeof(y)=='undefined') ) {return true;}
	  for(p in y) {
          if(typeof(x[p])=='undefined') {return true;}
      }

      for(p in x) {
          if(typeof(y[p])=='undefined') {return true;}
      }

      for(p in y) {
          if (y[p]) {
              switch(typeof(y[p])) {
                  case 'object':
                      if (compareObj(y[p],x[p])) { return true; } break;
                  case 'function':
                      if (typeof(x[p])=='undefined' ||
                          (y[p].toString() != x[p].toString()))
                          return true;
                      break;
                  default:
                      if (y[p] != x[p]) { return true; }
              }
          } else {
              if (x[p])
                  return true;
          }
      }

      return false;
    }

    var Register = function(){},
    Model = function(data){},
    Uniq = function()
    {
        this.items = {};
        //$(this.instances).trigger('garbage');
        //this.instances.push(this);
    },
    Collection = function(){},

    Url = Class.extend
    ({
        _construct: function(arg) 
        {
            this.data = !this.data ? { root: ''} : this.data;
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
        xfilter: function() 
        {
            this.data.xfilter = arguments.length > 1 ? $.makeArray(arguments).join(',') : $.isArray(arguments[0]) ? arguments[0].join(',') : arguments[0];
            return this;
        },
        root: function(root) 
        {
            this.data.root = root;
            return this;
        },
        get: function()
        {
            return this.data.root + this.data.url;
        },
        order: function(key, direction) 
        {
            this.data.order = direction+'='+key;
            return this;
        },
        filter: function(key, value) 
        {
            this.data.filter = key+'='+value;
            return this;
        },
        decorate: function(format)
        {
            this.data.url = format.replace(/(%s)/g, this.data.url);
        },
        options: function() 
        {
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
									$.support.cors = true;
                    var a;
                    if( source instanceof Url ) 
                    {
                        var options = $.extend(true, {}, predefinedOptions, self.options, userOptions, {data: data}, source.options());
						a = $.ajax(self.href(source.get()), options);
                    } 
                    else 
                    {
                        var options = $.extend(true, {}, predefinedOptions, self.options, userOptions, {data: data});
                        a = $.ajax(self.href(source), options);
                    }
                    self.reset();
                    
                    options.fail && a.fail(options.fail);
                    options.done && a.done(options.done);
                    options.always && a.always(options.always);
                    return a;
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
		_new: false,
        defaults: {},
        data: {},
        /*!
         * constructor
         */
        _construct: function(data, options)
        {
            this._clientId = uniqueIdCounter++;
            this.data = {};
            this.parseHash(data);
			this._new = true;
            var self = this.pushUnique ? this.pushUnique() : this;
            self._forDelete = false;
            self.clearChangeset();
            self._clientHash = null;
            if( options && typeof options == 'object' ) $.extend(self, options);
            if( typeof data == 'object' ) {
                self.parse(data);
				self._setExpiration();			
            }
            if(!$.isEmptyObject(self.changeset)) {
                //console.log('_constructor update', self.changeset);
                self.triggerHandler('update', self.changeset).clearChangeset();
            }

            return self;
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
            //console.log('sync');
            var self = this, ret = $.Deferred(), dataAdapter = function(){ return self.syncAdapter.request.apply(self.syncAdapter, arguments); };
            this.hash();
            // trigger an event before sync
            self.triggerHandler('sync');

            if( this._forDelete ) {// handle delete
                //console.log('delete');
                return dataAdapter(arguments[0] || this.href).remove().done(function()
                {
                    self._remove();
                });
            }
            if( this._clientHash ) // handle insert
            {
                //console.log('insert');
                var href = arguments[0] || this.href;
                return dataAdapter(href).insert(this.feed()).done(function(data)
                {
                    self._changed = false;
                    self.parse(data);
                    self._uniq && self._uniq.replace(self._clientHash, self.hash(), self);
                    self._clientHash = null;
                    self.triggerHandler('insert')
                        .Class.triggerHandler('insert', self);
                });
            }

            if( this._changed ) {// if changed do an update on the server and return
                //console.log('update');
                if(!$.isEmptyObject(this.changeset)) {
                    ret = (this.href && dataAdapter(this.href)
                            .update(arguments[1] ? this.feed() : this.feed('json', false, this.changeset))
                            .done(function()
                    {
                        self.triggerHandler('update', self.changeset).clearChangeset();
                    }));
                }
            }
			else {
				if( !(arguments[0] && arguments[0].force) && this.exTime && (  this.exTime > new Date) ) {
					if(!self.isDeleted()){
						self.triggerHandler('update');
					}
				}
            else
                // simply read data from server
                ret = (this.href && dataAdapter(this.href).read(arguments[0]).done(function(data)
                {
                    //console.log('Pull: ',$.extend({},data));
                    self.parse(data);
                    /**
                     * delete should come first of everything
                     * caz it can be some update data or read data that is telling is a deleted model.
                     */
                    if(self.isDeleted()){
                        //console.log('pull remove');
                        self._remove();
                    }
                    else if(!$.isEmptyObject(self.changeset)) {
                        //console.log('pull update: ',$.extend({},self.changeset));
                        self.triggerHandler('update', self.changeset).clearChangeset();
                    }
                    else {
                        //console.log('pull read');
                        self.clearChangeset().triggerHandler('read');
                    }
                }));
			}
			this._setExpiration();
            return ret;
        },
		_setExpiration: function()
		{
			this.exTime = new Date;
			this.exTime.setSeconds(this.exTime.getSeconds() + 5);
		},
        _remove: function()
        {
            this.triggerHandler('delete');
            this._uniq && this._uniq.remove(this.hash());
			//delete this;
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
         * overwrite this to add other logic upon parse complex type data
         */
        modelDataBuild: function(model)
        {
            return model
        },
        /*!
         * @param data the data to parse into the model
         */
        parse: function(data)
        {
            if(data instanceof Model) {
                data = data.data;
            }
            if(data._parsed)
                return;
            for( var i in data )
            {
                if( this.defaults[i] ) switch(true)
                {
					case (typeof this.defaults[i] === 'function') && (this.data[i] === undefined): // a model or collection constructor
						
                        var newModel = this.modelDataBuild(new this.defaults[i](data[i]));
                        if( !this._new && (newModel != this.data[i]) && !(newModel instanceof Collection) )
                            this.changeset[i] = newModel;
                        this.data[i] = newModel;

                        // fot model w/o href, need to make a collection since it's obviously
                        // an existing one and we don't need a new one
                        // TODO instanceof Model?
                        !data[i].href && this.data[i].relationHash && this.data[i].relationHash(data[i]);

                        continue;
                        break;

                    case $.isArray(this.defaults[i]): // a collection
                        this.data[i] = this.modelDataBuild(new Collection(this.defaults[i][0], data[i].href));
                        delete this.data[i];
                        continue;
                        break;

                    case this.defaults[i] instanceof Collection: // an instance of some colelction/model
                    case this.defaults[i] instanceof Model:
                        this.data[i] = this.defaults[i];
                        continue;
                        break;
                }
				else if( !this._new ) 
                {
                    if( $.type(data[i]) === 'object' )
                    {
                        if(compareObj(this.data[i], data[i]))
                            this.changeset[i] = data[i];
                    }
                    else if( this.data[i] != data[i] )
                    {
                        this.changeset[i] = data[i];
                    }
                }
                if( $.type(data[i]) === 'object' && $.type(this.data[i]) === 'object' )
                    $.extend(true, this.data[i], data[i]);
                else
                    this.data[i] = data[i];
            }
			this._new = false;
            data._parsed = true;
        },
        parseHash: function(data)
        {
            if( typeof data == 'string' )
                this.href = data;
			else if( data && data.href !== undefined) {
                this.href = data.href;
				delete data.href;
			}
            else if(data && ( data.id !== undefined) && (this.url !== undefined))
                this.href = this.url + data.id;
            return this;
        },
		isChanged: function()
		{
			return !$.isEmptyObject(this.changeset);
		},
        clearChangeset: function()
        {
            this._changed = false
            this.changeset = {};
            return this;
        },
        get: function(key)
        {
            return this.data[key];
        },
        set: function(key, val, options)
        {
            var data = {};
            if( $.type(key) === 'string' )
                data[key] = val;
            else
            {
                data = key;
                options = val;
            }
            options = $.extend({},{ silent: false}, options);
            this.clearChangeset().parse(data);
            this._changed = true;
            if(!$.isEmptyObject(this.changeset)) {
                if(!options.silent)
                    this.triggerHandler('set', this.changeset);
            }

            return this;
        },
        /*!
         * used for new models not yet saved on the api
         */
        _getClientHash: function()
        {
            if( !this._clientHash ) this._clientHash = "mcid-"+String(this._clientId);
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
         * used to remove events from this model
         */
        off: function(evt, handler)		
		{
			$(this).off(evt, handler);
			return this;
		},
        /*!
         * used to place events on this model,
         * scope of the call method is sent as obj argument
         */
        on: function(evt, handler, obj)
        {
            if(obj === undefined) {
                $(this).off(evt, handler);
				$(this).on(evt, handler);
			}
            else {			
				$(this).on(evt, function(){
                    handler.apply(obj, arguments);
				});
			}
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
            for( var key in this.items )
            {
                if( this.items[key]._exTime && this.items[key]._exTime < new Date )
                {
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
        newly.prototype.Class = newly;
        newly.on = function(event, handler, obj)
        {
            $(newly).on(event, function(){ handler.apply(obj, arguments); });
			return newly;
        };
        newly.off = function(event, handler)
        {
            $(newly).off(event, handler);
			return newly;
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
                        buildOptions = (function(args){ return function(){ this.options = args; if(args.href) this.href = args.href; }})(arguments[i]);
                        break;
                }
            }
            // callbacks in order
            buildOptions.call(this);
            buildData.call(this);
            options = $.extend({}, { init: true}, this.options);
            options.init && this.init.apply(this, arguments);

        },
        init: function(){},
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
        forwardEach: function(fn, scope){
            this._list.forEach(fn, scope);
        },
        reverseEach: function(fn, scope)
        {
            for(var i = this._list.length; i > 0; ++i) {
                fn.call(scope || this, this[i], i, this);
            }
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
                    var data = self.parse(data), changeset = [], count = self._list.length;
                     // important or it will infiloop
                    for( var i=0; i < data.list.length; i++ )
                    {
                        var model = false;
                        for( var j=0; j<count; j++ ) {
							if( data.list[i].hash() == self._list[j].hash() )
                            {
								model = data.list[i];
                                break;
                            }
						}
                        if( !model ) {
                            self._list.push(data.list[i]);
                            changeset.push(data.list[i]);
                        }
                        else {
                            self._list[j].parse(model.data);
                            if( model.isDeleted() ) {
                                model._remove();
                            } else if( model.isChanged() ){
								changeset.push(data.list[i]);
							}
                            else {
                                model.on('delete', function(){ self.remove(this.hash()); })
                                        .on('garbage', function(){ this.desynced = true; });
                            }
                        }
                    }
                    self.desynced = false;
					/**
					 * If the initial data is empty then trigger READ event
					 * else UPDATE with the changeset if there are some
					 */
					if( ( count === 0) ){
						//console.log('read');
						self.triggerHandler('read');
                    } else {                    
                        /**
                         * Trigger handler with changeset extraparameter as a vector of vectors,
                         * caz jquery will send extraparameters as arguments when calling handler
                         */
                        //console.log('update');
						self.triggerHandler('update', [changeset]);
					}
                }));
        },
        /*!
         * overwrite this to add other logic upon parse complex type data
         */
        modelDataBuild: function(model)
        {
            return model;
        },
        /*!
         *
         */
        parse: function(data)
        {
            if(data.parsed) {
                return data.parsed;
            }
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
            for( var i in theData ) {
				if(theData.hasOwnProperty(i))
                list.push( this.modelDataBuild(new this.model(theData[i])) );
            }
            data.parsed = {list: list, total: data.total};
            return data.parsed;
        },
        insert: function(model)
        {
            this.desynced = false;
            if( !(model instanceof Model) ) model = this.modelDataBuild(new this.model(model));
            this._list.push(model);
            model.hash();
            var x = model.sync(this.href);
            return x;
        },
		/*!
         * used to remove events from this model
         */
        off: function(evt, handler)		
		{
			$(this).off(evt, handler);
			return this;
		},
		/*!
         * used to place events on this model,
         * scope of the call method is sent as obj argument
         */
        on: function(evt, handler, obj)
        {
            if(obj === undefined) {
                $(this).off(evt, handler);
				$(this).on(evt, handler);
			}
            else {			
				$(this).on(evt, function(){
                    handler.apply(obj, arguments);
				});
			}
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

    Collection.extend = cextendFnc = function(props)
    {
        var newly;
        newly = Class.extend.call(this, props);
        newly.extend = cextendFnc;
        if(options && options.register)
            Collection[options.register] = newly;
        return newly;
    };
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
            options.events && this.resetEvents();
        },
        _ensureElement: function()
        {
            var className = this.attributes.className,
                id = this.attributes.id,
                el ='';
            if(!$(this.el).length) {
                if($.type(this.el) === 'string') {
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
            } else
				this.el = $(this.el);
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
						//console.log($.type(self[fn]), ', ', this.getEvent(evnt), ', ',selector, ', ',fn);
                        if($.isFunction(self[fn])) {
                            $(this.el).on(this.getEvent(evnt), selector, self[fn].bind(self));
                        }
                    }
                }
            }
        },
        undelegateEvents: function()
        {
            $(this.el).off(this.getNamespace());
			return this;
        },		
        getEvent: function(evnt){
            return evnt + this.getNamespace();
        },
        getNamespace: function()
        {
            return '.'+this.getProperty('namespace');
        },
        render: function(){

            this.delegateEvents();
            return this;
        },
        remove: function()
        {
			$(this.el).remove();
			this.destroy();
            return this;
        },
		destroy: function()
		{
            if(this.model)
				this.model.trigger('destroy');
			if(this.collection)
				this.collection.trigger('destroy');
			return this;
		},
		checkElement: function()
		{
			//console.log('Undefined: ',(this.el === undefined));
			
			if(this.el === undefined)
				return false;
			
			//console.log('Selector: ',this.el.selector, ' length: ',($(this.el.selector).length === 1));
			
			if((this.el.selector !== undefined) && (this.el.selector != ''))
				return ($(this.el.selector).length === 1);			

			//console.log('Visible: ',$(this.el).is(':visible'));

			return ($(this.el).is(':visible'));
			
			//console.log('Last: ',this.el, ' length: ',($(this.el).length === 1));
			
			return ($(this.el).length === 1);
			
		},
        setElement: function(el)
        {
            this.undelegateEvents();
            var newel = $(el), prevData = this.el.data();
            this.el.replaceWith(newel);
            this.el = newel;
            this.el.data(prevData);
            this.delegateEvents();
            return this;
        },
        resetElement: function(el)
        {
            this.el = $(el);
            this._ensureElement();
            this.delegateEvents();
        }
    });
    
    return { Model: Model, Collection: Collection, Sync: Sync, UniqueContainer: Uniq, View: View, Url: Url, Register: Register};
});
