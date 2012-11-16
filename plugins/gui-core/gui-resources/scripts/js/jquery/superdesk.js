define(['jquery','jquery/rest','history','history/adapter'], function ($) {

var superdesk = 
{
    apiUrl: typeof config !== 'undefined' ? config.api_url : '', 
	/*!
	 * repository for templates
	 */
	tmplRepo: $('<div />'),
	/*!
	 * Loads template files via ajax and extracts the templates
	 * 
	 * @param string path 
	 * 	the url from which to load templates
	 * @param string selector 
	 * 	optional, selector to use to match templates in loaded file
	 * @returns $.Deferred
	 */
	getTmpl: function(path)
	{
		var tplSelector = typeof arguments[1] != 'undefined' ? arguments[2] : "script[type='text/x-jQuery-tmpl']", 
			dfd = new $.Deferred;
		$.ajax(path, {dataType: 'html'}).done(function(html)
		{ 
			var templates = [];
			$(html).each(function(i, elem){ if($(elem).is(tplSelector)) templates.push(elem); });
			superdesk.tmplRepo.append(templates);
			dfd.resolve(templates);
		});
		return dfd;
	},
	layouts: {},
	/*!
	 * load layout to superdesk object layouts
	 * @param string path 
	 * 	layout path
	 * @param string name 
	 * 	layout name
	 */
	loadLayout: function(path, name)
	{
		return $.ajax( superdesk.apiUrl+path, {dataType: 'html'})
			.done(function(data)
			{
				// need to wrap it in a <div /> tag for $ selector to work
				var layoutObject = $('<div>'+data+'</div>');
				if( typeof name == 'string')
					superdesk.layouts[name] = layoutObject;
				else
					name = layoutObject;
				
				return layoutObject;
			});
	},
	
	loaderTO: null,
	showLoader: function()
	{
	    $('#navbar-top .loader').css('display', 'block');
        this.loaderTO = setTimeout(function(){ $('#navbar-top .loader').css('display', 'none'); }, 20000);
	},
	hideLoader: function()
	{
	    $('#navbar-top .loader').css('display', 'none');
	    clearTimeout(this.loaderTO);
	},
	
	layoutPlaceholder: '#area-main',
	applyLayout: function(tmpl, data, callback)
	{
	    /*$(this.layoutPlaceholder).nextAll().each(function()
	    {
	        console.log(this);
	    });*/
	    return $(this.layoutPlaceholder).tmpl(tmpl, data, callback);
	},
	/*!
	 * cache repo
	 */
	cache: {actions: {}, scripts: {}, test: {}},
	ACTIONS_PATH_SEP: '.',
	/*!
	 * @param string path 
	 * @returns $.Deferred()
	 */
	getActions: function(path)
	{
	    var dfd = $.Deferred(),
	    searchCache = function()
	    {
	        var results = [], searchForSubs = false, searchPath = path; 
	        if( path.lastIndexOf('*') === path.length-1 )
	            searchPath = path.substr(0, path.length-1);

	        for( var i in superdesk.cache.actions )
                if( superdesk.cache.actions[i].Path.indexOf(searchPath) === 0 )
                    results.push(superdesk.cache.actions[i]);

	        return results;    
	    };
	    var cachedResults = searchCache();
	    if( cachedResults.length === 0 )
		{
			new $.rest('GUI/Action?path='+path)
				.done(function(actions)
				{ 
				    for(var i in actions)
                        superdesk.cache.actions[actions[i].Path] = actions[i];
					dfd.resolve(searchCache());
				});
			return dfd;
		}
		return dfd.resolve(cachedResults);
	},
	
	getAction: function(path)
	{
	    var dfd = $.Deferred();
        if( !superdesk.cache.actions[path] )
        {
            var searchPath = path.substr(0, path.lastIndexOf(superdesk.ACTIONS_PATH_SEP)); 
            new $.rest('GUI/Action?path='+searchPath+'.*')
                .done(function(actions)
                { 
                    for(var i in actions)
                        superdesk.cache.actions[actions[i].Path] = actions[i];
                    dfd.resolve(superdesk.cache.actions[path]);
                });
            return dfd;
        }
        return dfd.resolve(superdesk.cache.actions[path]);
	},
	/*!
	 * 
	 */
	navigation: 
	{
	    _repository: {},
	    _base: '',
	    _startPathname: '',
	    _titlePrefix: '',
	    getBase: function()
	    {
	        return this._base;
	    },
	    getStartPathname: function()
        {
            return this._startPathname;
        },
        consumeStartPathname: function()
        {
            var r = this._startPathname;
            this._startPathname = '';
            return r;
        },
        /*!
         * bind a callback on history state or execute if already bound
         */
        bind: function(href, callback, title)
        {
            var History = window.History;

            if( $.trim(href) != '' && this._repository[href]  )
            {
                History.replaceState({href: href}, 
                        title ? this._titlePrefix + title : null, 
                        this._base + (!config.server_tech ? '?'+href : href));
                callback.call();
                return callback;
            }
            
            this._repository[href] = callback;
            
            History.pushState({href: href}, 
                    title ? this._titlePrefix + title : null, 
                    this._base + (!config.server_tech ? '?'+href : href));
            return callback;
        },
        /*!
         * app base url:
         *  check for standard base tag in html or just get the current url
         */
        init: function(callback)
        {
            var History = window.History, 
                State = History.getState(),
                self = this,
                baseTag = $('base');
            
            History.options.debug = true;
            this._base = baseTag.length ? baseTag.attr('href') : History.getPageUrl().split('?')[0].split('#')[0];
            this._startPathname = window.History.getPageUrl().replace(this._base, '')
                                    .replace(/^\/+|\/+$/g, '').replace(/^\?+/g, '').replace(/#/g, '');
            var triggered;
            History.Adapter.bind( window, 'statechange', function()
            {
                var State = History.getState();
                (self._repository[State.data.href])();
                triggered = true;
            });
            
            if( typeof callback === 'function' )
            {
                this._repository[''] = callback;
                this._base = this._base;
                History.pushState( {href: ''}, $(document).prop('title'), this._base );
                !triggered && History.Adapter.trigger( window, 'statechange' );
            }
        }
	},
	/*!
	 * 
	 */
	presentation: function(script, layout, args)
	{
		var _setScript = function(value){ script = value; };
		this.setScript = function(value){ _setScript(value); return this; };
		this.getScript = function(){ return script; };
		
		var _setLayout = function(value){ layout = value; };
		this.setLayout = function(value){ _setLayout(value); return this; };
		this.getLayout = function(){ return layout; };
		
		var _setArgs = function(value){ args = value; };
		this.setArgs = function(value){ _setArgs(value); return this; };
		this.getArgs = function(){ return args; };
		
		var script = script,
			layout = layout || null,
			args = args || null,
			self = this;
		
		/*!
		 * Loads and applies script to a layout object
		 * 
		 * @param string scriptPath 
		 * @param object layoutObject 
		 * @param object additional
		 * 	additional parameters to be passed
		 */
		this.run = function()
		{
			if(arguments[0]) _setScript(arguments[0]); // set script
			if(arguments[1]) _setLayout(arguments[1]); // set layout
			if(arguments[2]) _setArgs(arguments[2]); // set args
			
			var dfd = $.Deferred();
			dfd.done(function(scriptText)
			{
				// TODO additional security checking here
				(new Function('layout', 'args', scriptText)).call(self, layout, args);
			});
			if( !superdesk.cache.scripts[script] )
			{
				$.ajax(superdesk.apiUrl + '/' + script, {dataType: 'text'})
					.done(function(data)
					{
						superdesk.cache.scripts[script] = data;
						dfd.resolve(data);
					});
				return dfd;
			}
			return dfd.resolve(superdesk.cache.scripts[script]);
		};
	}
};
superdesk.presentation.prototype = 
{
	view:
	{
		prefix: function(){ return superdesk.apiUrl+'/content/gui/superdesk/'; },
		load: function(template)
		{
			return superdesk.getTmpl( (typeof this.prefix == 'function' ? this.prefix() : this.prefix) + template);
		},
		render: function(selector, data)
		{
			if(typeof selector == 'string') var tmpl = $(selector, superdesk.tmplRepo);
			else var tmpl = selector;
			return $($.tmpl(tmpl, data));
		}
	},
	form:
	{
		add: function(html, nodeName)
		{
			if(!nodeName) return html;
			$(html).find('input, textarea, select').each(function()
			{
				var name = $(this).attr('name') || '';
				$(this).attr('name', name.replace(/^([^\[]+)/, nodeName+'[$1]'));
			});
			return $(html);
		}
	}
};

$.extend($, {superdesk: superdesk});
return superdesk;
});