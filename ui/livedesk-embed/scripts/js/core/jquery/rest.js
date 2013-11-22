define('jquery/rest',['jquery', 'jquery/utils'], function ($) {
	var dfdManager = 
	{
		add: function(parentDfd, childDfd)
		{
			childDfd.children = [];
			if(typeof parentDfd.children == 'undefined') parentDfd.children = [];
			parentDfd.children.push(childDfd);
		},
		stop: function(dfd)
		{
			if(typeof dfd.children != 'undefined')
				for(var i in dfd.children)
					dfdManager.stop(dfd.children[i]);
			dfd.reject();
		}
	};
	
	function chainable(fn, name)
	{
		this.deferred = $.Deferred();
		//this.deferred.progress(function(){ console.log('progress '+this.name+' with', arguments) })
		this.fn = fn;
		this.name = name;
	};
	chainable.prototype.promise = function()
	{
		return this.deferred.promise();
	};
	chainable.prototype.invoke = function()
	{
		this.fn.apply(this, arguments)
		return this;
	};

    /*!
     * Private method to get the url
     */
    function getUrl(data)
    {
		var aux = "";
		if(data !== undefined) {
			for(i in data) {
				aux = aux+'&'+i+'='+data[i];
			}
			aux = '?'+aux.substring(1,aux.length);
		}
        if( (this.lastUrl.substr(0,4).toLowerCase() === 'http') ||
            (this.lastUrl.substr(0,5).toLowerCase() === 'https') ||
            (this.lastUrl.substr(0,2) === '//') ) {
            return this.lastUrl+aux;
        } else if(this.lastUrl.substr(0,1) === '/' ) {
            return this.config.apiUrl+this.lastUrl+aux;
        } else {
            return this.config.apiUrl+this.config.resourcePath+this.lastUrl+aux;
        }
    }
	/*!
	 * construct
	 */
	function resource()
	{
	    arguments.length && this._construct.apply(this, arguments);
	};
	
	resource.prototype = 
	{
	    _: '',
        getData: [],
        lastAdded: {},
        lastUrl: '',
        job: [],
        initXFrom: false,
        respArgs: null,
        dataChanged: false,
        initData: undefined,
        fromData: undefined,
        getData: [],
        _construct: function()
        {
            var self = this,
                extractListData = this.extractListData;
            this.getData = [];
            if( typeof arguments[0] == 'string' )
            {
                self.lastUrl = arguments[0];
                self.request({url :
                    arguments[0].indexOf('http://') !== -1 ? arguments[0] :
                    self.config.apiUrl+self.config.resourcePath+arguments[0] });
                var resolve = null;
                self.initData = new chainable( function()
                {
                    if( resolve && !self.dataChanged ) 
                    {
                        this.deferred.resolve(resolve); 
                        return ret;
                    };
                    
                    if( typeof this.request != 'undefined' ) self.request(this.request);
                    return self.doRequest()
                        .pipe(function(data)
                        {
                            resolve = extractListData(data);
                            self.dataChanged = false;
                            return resolve;
                        })
                        .then(this.deferred.resolve, this.deferred.reject);
                }, 'initData from ajax');
            }
            else
            {
                var ret = extractListData(arguments[0]);
                this.initData = new chainable(function()
                { 
                    this.deferred.resolve(ret); return ret; 
                }, 'initData with data');
            }
            
            this.lastAdded = this.initData;
            
            this.fromData = new chainable(function(data){ this.deferred.resolve(data); }, 'fromInit');
            var fromData = this.fromData,
                self = this;
            
            fromData.promise().always(function(){ self.initXFrom = false; })
            self.initXFrom = true;
            $.when(this.initData).then(function()
            {
                fromData.invoke.apply(fromData, arguments);
            }, fromData.deferred.reject );
            
            if(arguments[1]) this.name = arguments[1];
        },
        extractListData: function(data)
        {
            var ret = data;
            if( !Array.isArray(data) ) for( i in data ) 
            {
                if( Array.isArray(data[i]) )
                {
                    ret = data[i];
                    break;
                }
            }
            return ret;
        },
	    config:
	    {
	        resourcePath: '/resources/',
	        apiUrl: ''
	    },
        requestOptions: 
        {
            dataType: 'json',
            type: 'get',
            headers: { 'Accept' : 'text/json' } 
        },
		chainable: chainable,
	
		/*!
		 * get item from the already existing list
		 */
		from: function(key)
		{
			var self = this,
				args = arguments;
			
			this.fromData = new chainable( function(list)
			{
				var found = false;
				for( var item in list )
				{
					if( typeof key != 'object' && item != key ) continue;
					found = list[item];
					// for each key check if exists and is the value	
					for( keyName in key )
						if(!(keyName in list[item]) || list[item][keyName] != key[keyName])
						{
							found = false;
							break;
						}
					if( found ) break;
				}
				
				if( !found || typeof found.href == 'undefined' ) return this.deferred.reject();
				var fromUrl = found.href;
					
				if( args.length > 1 ) 
				{
					if(typeof args[1] == 'function')
						fromUrl = args[1](found); // filter function for complex structures
					if(typeof args[1] == 'object')
						self.request(args[1]);
					if(typeof args[2] == 'object')
						self.request(args[2]);
				}
				
				if( typeof this.request != 'undefined' )
					self.request(this.request);
				
				self.lastUrl = fromUrl;
				return self
					.doRequest(fromUrl)
					.pipe(function(data)
					{ 
						self.fromData.fn = function()
						{ 
							this.deferred.resolve(data); 
							return data; 
						};
						return data;
					})
					.then(this.deferred.resolve, this.deferred.reject);
				
			}, "from "+key);
			
			var fromData = this.fromData;
			this.lastAdded = fromData;

			if(!self.initXFrom)
			{
				self.iniXFrom = true;
				$.when(this.initData).then(function(){ fromData.invoke.apply(fromData, arguments); }, fromData.deferred.reject );
			}
			
			if( typeof this.insideJob != 'undefined' )
				this.insideJob.push(fromData);
			
			return this;
		},
	
		/*!
		 * register an operation to obtain a key value from an object node
		 * obtained by the last operation either from or construct
		 */
		get: function(key)
		{
			var self = this;
			var args = arguments;
			var getData = new chainable( function(data) 
			{
				var node;
				if( !Array.isArray(data) && $.isObject(data) )
					if( Object.keys(data).length == 1 )
					{
						for( var i in data )
							if( key in data[i] )
								node = data[i][key]
					}
					else if(typeof data[key] != 'undefined') node = data[key];
	
				if(typeof node == 'undefined') 
				{
				    this.deferred.resolve(null);
					return false;
				}
	
				// assume that we only have a href property provided and we need to follow it to get the entity
				if(typeof node.href == 'string' && Object.keys(node).length == 1)
				{
					var dfd = this.deferred;
					if(typeof args[1] != 'undefined' )
						self.request(args[1]);
					
					if( typeof this.request != 'undefined' )
						self.request(this.request);
					
					self.lastUrl = node.href;
					var ajax = self.doRequest(node.href)
						.then(this.deferred.resolve, this.deferred.reject);
					return ajax;
				}
				// assume we have all/the filtered properties
				else
					return this.deferred.resolve(node);
			}, "get "+key);
			
			this.getData.push(getData);
			this.lastAdded = getData;
			
			$.when(this.fromData).then(function(){ getData.invoke.apply(getData, arguments); }, getData.deferred.reject );
			
			if( typeof this.insideJob != 'undefined' )
				this.insideJob.push(getData);
			
			return this;
		},
		
		/*!
		 * execute operations and optionally execute a callback
		 */
		done: function()
		{
			if( !this.getData.length )
			{
				var getInit = new chainable(function(data)
				{
					this.deferred.resolve(data);
				}, 'getInit');
				getInit.isInit = true;
				this.getData = [getInit];
				$.when(this.fromData).then(function(){ getInit.invoke.apply(getInit, arguments); }, getInit.deferred.reject );
			}
					
			var self = this,
				name = arguments[1];
			
			if( typeof arguments[0] == 'function' )
			{
				var callback = arguments[0],
					failCallback = $.noop;
				
				if(typeof arguments[1] == 'function')
					failCallback = arguments[1];
				
				$.when.apply($, this.getData).then(function()
				{
					var args = $.makeArray(arguments);
					if( typeof self.spawned != 'undefined' )
						args = args.concat(self.spawned);
					var result = callback.apply(self, args);
				}, 
				function()
				{
					failCallback.apply(self, arguments);
				})
				.always(function() // we need to reset at least initData for future chains..
				{
					self.initData = new chainable(self.initData.fn, 'reset');
					self.fromData = new chainable(self.fromData.fn, 'reset');
					self.initXFrom = true;
					$.when(self.initData).then(function()
					{ 
						self.fromData.invoke.apply(self.fromData, arguments); 
					}, self.fromData.deferred.reject );
				});	
			}
			
			var trigger = $.Deferred();
			trigger.resolve();
			var initData = this.initData;
			$.when(trigger).then(function(){ initData.invoke.apply( initData, arguments ); });
			self.getData = [];
			return this;
		},
		
		resetJob: function()
		{
			if(typeof this.job == 'undefined') return this;
			for(var i in this.job)
				this.job[i].deferred.reject();
			this.job = [];
			return this;
		},
		
		registerToJob: function(job)
		{
			this.insideJob = job;
			return this;
		},
		
		/*!
		 * execute this callback regardless of fail or done get operations
		 */
		always: function(callback)
		{
			var self = this;
			var dfd = $.Deferred();
			$.when(dfd).then(function(data)
			{ 
				if(typeof callback == 'function')
					callback.apply(self, data);
			});
			var progress = this.getData.length;
			var args = [];
			$(this.getData).each(function(i, fn)
			{
				fn.promise().always(function()
				{
					progress--;
					if(arguments.length > 1) // if more than 1 argument put them in an array
						args.splice(i, 0, arguments);
					else // else just the single one 
						args.splice(i, 0, arguments[0]);
					if(!progress) 
						dfd.resolve(args);
				});	
			})
			return this;
		},
		
		/*!
		 * spawn a new resource rom the last get method called
		 */
		spawn: function()
		{
			var self = this;
			$.when(this.lastAdded).pipe(function(data)
			{
				self.spawned = new resource(data, 'spawned');
				self.spawned.lastUrl = self.lastUrl;
				// TODO add backreference or not?
				return data;
			});
			return this;
		},
		
		/*!
		 * make the request
		 * @param string url
		 */
		doRequest: function()
		{
			if(typeof arguments[0] == 'string') this.request({url: arguments[0]});
			var self = this,
				ajax = $.ajax(this.requestOptions)
				.fail(function(){ $(self).trigger('failed', arguments); })
				.always(function(){ self.respArgs = arguments[0]; });
			if(!this.keepXFilter)
				delete this.requestOptions.headers['X-Filter'];
			return ajax;
		},
		responseArgs: function()
		{
			return this.respArgs;
		},
		/*!
		 * 
		 */
		update: function(data, url)
		{
		    if( this.lastAdded.request )
		        $.extend(this.lastAdded.request.headers, {'X-HTTP-Method-Override': 'PUT'});
		    else
		        this.lastAdded.request = {headers: {'X-HTTP-Method-Override': 'PUT'}};
			this.request({type: 'post', headers: this.lastAdded.request.headers, data: data});
			return this.doRequest(url ? url : getUrl.apply(this,[{'X-HTTP-Method-Override': 'PUT'}]));
		},
		select: function(data, url)
		{
			this.request({type: 'get', data: data, headers: this.lastAdded.request ? this.lastAdded.request.headers : {}});
			return this.doRequest(url ? url : getUrl.apply(this));
		},
		/*!
		 * 
		 */
		insert: function(data, url)
		{
			this.request({type: 'post', data: data, headers: this.lastAdded.request ? this.lastAdded.request.headers : {}});
			return this.doRequest(url ? url : getUrl.apply(this));
		},
		/*!
		 *
		 */
		delete: function(data, url)
		{
		    if( this.lastAdded.request )
		        $.extend(this.lastAdded.request.headers, {'X-HTTP-Method-Override': 'DELETE'});
		    else
		        this.lastAdded.request = {headers: {'X-HTTP-Method-Override': 'DELETE'}};
			this.request({type: 'get', headers: this.lastAdded.request.headers, data: data});
			return this.doRequest(url ? url : getUrl.apply(this,[{'X-HTTP-Method-Override': 'DELETE'}]));
		},
		
		/*!
		 * extend request options
		 */
		request: function(options)
		{
			if( options.hasOwnProperty('data') ) this.dataChanged = true;
			this.requestOptions = $.extend(true, {}, this.requestOptions, options);
			return this;
		},
		
		/*!
		 * reset request option data, optionally by key
		 */
		resetData: function(key)
		{
			if( !this.requestOptions.data ) return this;
			if( typeof key == 'undefined' ) {
				delete this.requestOptions.data;
				return this;
			}
			delete this.requestOptions.data[key];
			return this;
		},
		
		/*!
		 * 
		 */
		xfilter: function(value)
		{
			this.lastAdded.request = { headers: { 'X-Filter' : value } };
			return this;
		}
	};
	
	$.extend($, {rest : resource});
	
	
	function restAuth()
	{  
	    resource.apply(this, arguments);  
	}  
	
	restAuth.prototype = Object.create(new resource(), 
	{  
	    _construct: { value: function()
	    {
	        //this.config = $.extend({}, this.config, {resourcePath: '/resources/my/'});
	        this.config = $.extend({}, this.config, {resourcePath: '/resources/'});
            //this.requestOptions.headers.Authorization = 111;
	        resource.prototype._construct.apply(this, arguments);
	        
	    }, enumerable: true, configurable: true, writable: true }  
	});  
	    
    $.extend($, {restAuth : restAuth});
});