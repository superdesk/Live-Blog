define(['jquery', 'utils/extend', 'utils/class'], function()
{
    var Sync = 
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

	var Classed = Class.extend({
		getProperty: function(prop)
		{
			if (!this[prop]) return null;
			return $.isFunction(this[prop]) ? this[prop]() : this[prop];
		}
	});

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
    var uniq = new Uniq;
	
	var View = Classed.extend({
		_constructor: function(prop)
		{
			var self = this;
			for (var name in prop) {
			  this[name] = prop[name];
			}
			self.init();
			self.render();
			self.delegateEvents();
		},
		namespace: 'view',
		init: function(){ return this; },
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
						if($.isFunction(self[fn]))
							$(selector, this.el).on(evnt + this.getNamespace(), self[fn].bind(self));
					}else if($.isArray(other)) {
						fn = other[0];
						if($.isFunction(other[1]) && (other.length>1) && (other.length<=2)) {
							sel = other[0];
							fn = other[1];
							if($.isFunction(self[fn]))
								$(selector, this.el).on(evnt + this.getNamespace(), sel, self[fn].bind(self));
						} else if($.isFunction(other[2]) && (other.length>2)) {
							dat = other[0];
							sel = other[1];
							fn = other[2];
							if($.isFunction(self[fn]))
								$(selector, this.el).on(evnt + this.getNamespace(), sel, dat, self[fn].bind(self));
						} else {
							if($.isFunction(self[fn]))
								$(selector, this.el).on(evnt + this.getNamespace(), self[fn].bind(self));
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
		render: function(){ return this; },
		remove: function()
		{
			$(this.el).remove();
			return this;
		},
		setElement: function(el)
		{
			this.el = el;
		}
	});
	var Model = Classed.extend({
        changed: false,
        defaults: {},
        data: {},
        /*!
         * constructor
         */ 
        _construct: function(data, options)
        {
			console.dir(data);
			console.dir(options);
            if( typeof data == 'string' ) this.href = data;
            if( typeof data == 'object' ) $.extend(this.data, data);
            if( options && typeof options == 'object' ) $.extend(this.options, options);
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
        hash: function(){ return this.data.href; },
        /*!
         * used to relate models. a general standard key would suffice
         */
        relationHash: function(){ return this.data.Id; }
    });
	
	var UniqModel = Model.extend({
		_constructor: function() {
			if((this.uniq !== undefined) && (this.hash() !== undefined)) {
				if(typeof this.uniq === 'string') {
					return uniq.get(new Uniq, this.uniq).get(this,this.hash());
				} else {
					return this.uniq.get(this,this.hash());
				}
			}
		}
	});

    var Collection = Classed.extend({
        _list: [],
		model: Model,
        dataAdapter: Sync.dataAdapter,		
		_constructor: function(){
			var buildData = buildOptions = function(){ void(0); },
				self = this;
				
			for( var i in arguments ) 
			{
				if( arguments[i] instanceof Model)
				{
					this.model = arguments[i];
					continue;
				}
				if( $.isArray(arguments[i]))
					this._list = this.parse(arguments[i]);
				if( $.isPlainObject(arguments[i])) {
					this[i] = arguments[i];
				}
			}
		},
        get: function(key)
        {
            for( var i in this._list ) if( key == this._list[i].hash() ) return this._list[i];
            return undefined;
        },
        sync: function()
        {
            var self = this;
            return (this.url && 
                this.dataAdapter(this.url).read(function(data)
                {
                    self.parse(data);
                    $(self).triggerHandler('update');
                    $(self._list).triggerHandler('update');
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
    });
        
    return { Model: Model, Collection: Collection, View: View };
})