/**
 * @author Mihai Balaceanu <mihai.balaceanu@sourcefabric.org>
 * @package Newscoop
 * @subpackage Components
 * @copyright 2011 Sourcefabric o.p.s.
 * @license http://www.gnu.org/licenses/gpl.txt
 *
 * After the first call with at least some blank options object
 * you will be able to call it without any arguments and retrieve the datatable object
 * having available:
 * 		- addOption method to extend the first options
 * 		- addPlugin method to extend the plugins
 * 		- refresh method to recall the last data request
 * 		- options object
 * 		- plugins object
 *
 * @todo maybe add some default templates or escape errors on none found at data request..
 */
jQuery.fn.datatable = function( options, userPlugins )
{
	var defaults 	=
	{
		dataSource : location.href,
		rowTemplate : null,
		headerTemplate : null,
		footerTemplate : null,
		dataSuccess : function(response)
		{
			if( typeof response.data == 'undefined' ) { // exit if we have no data
				return false;
            }
            
            if( response.data.code ) {
                showNotification(response.data.message);
                $(this).trigger('datatable-data-close');
                return false;
            }
            var objTable = $(this).find('table');
			var objBody = objTable.find('tbody'); // format and set data per cells
			objBody.remove();
            objBody = $('<tbody/>').appendTo(objTable);
			for( dataRow in response.data )
			{
                                var data = response.data[dataRow];
                                data['index'] = dataRow;
                                $($.tmpl( $('#'+options.rowTemplate), data, $(this).data('data-definitions') ))
                                        .iff(function(){return $(this).is('tbody');})
                                            .appendMe(objTable)
                                        .els()
                                        .iff(function(){return $(this).is('tr');})
                                            .appendMe(objBody)
                                        .els()
                                            .appendMe('<tr/>').appendTo(objBody)
                                        .end();
			}
			$(this).trigger( 'datatable-data-success', [response] );
		},
		dataError : function(jqXHR, textStatus, errorThrown)
		{
			if( typeof console != 'undefined' ) console.exception(errorThrown);
			$(this).trigger('datatable-data-error');
		}
    };

	// params for request
	var _requestData = {};
    var _requestVector = {};

	// request function
	var dataRequest = function()
	{
        $(this).trigger( 'datatable-data-refresh');
		$.ajax
		({
			url : options.dataSource,
			data : $.extend( {}, { 'format' : 'json' }, _requestData, _requestVector ) ,
			dataType : 'json',
			context : this,
			success : options.dataSuccess,
			error : options.dataError
		});
	};

	var plugins =
	{
        loader : 
        {
            init: function()
            {
                plugins.loader._init.call(this);
            },
            _init : function()
            {
                $(this).bind('datatable-init',function(){
                    if( options.loaderTemplate ) {
                        $(this).prepend($.tmpl($('#'+options.loaderTemplate), {}));
                    }
                })
                .bind('datatable-data-success',function(){
                    plugins.loader.toggleOverlay.call(this, false);
                })
                .bind('datatable-data-close',function(){
                    plugins.loader.toggleOverlay.call(this, false);
                })
                .bind('datatable-data-refresh',function(){
                    plugins.loader.toggleOverlay.call(this, true);
                });
            },
            toggleOverlay: function(sw){                                
				$(this).find('.loading-message:first').html($(this).data('loading-message'));
				if(sw) {
                    $(this).find('.loading-overlay').show();
                }
                else
                    $(this).find('.loading-overlay').hide();
            },
			addMessage: function(msg){
					console.log(msg,msg.length);
					msgBox = $(this).find('.loading-message');
					if(!msgBox.length) {
						msgBox = $('<div class="loading-message"></div>');
						aux = $(this).find('.loading-overlay');
						aux.append(msgBox);
					}
					msgBox.html(msg);
			}
        },
		search :
		{
			init : function()
			{
				plugins.search._init.call(this);
			},
			_init : function()
			{
				var searchbox = $(this).find('.header .search input[type=text]');
				var searchsubmit = $(this).find('.header .search input[type=submit]');
				var searchreset = $(this).find('.header .search input[type=reset]');

				searchbox.bind( 'keyup.datatable', { 'datatable': this }, plugins.search.searchboxKeyup );
				searchsubmit.bind( 'click.datatable', { 'datatable' : this, 'searchbox' : searchbox }, plugins.search.searchSubmit );
				searchreset.bind( 'click.datatable', { 'datatable' : this, 'searchbox' : searchbox }, plugins.search.searchReset );
			},
			searchboxKeyup : function(evt)
			{
				if( typeof evt.data.datatable == 'undefined' ) {
					return false;
				}

				// return on empty value
				if( $.trim($(this).val()) == '' ) return false;

				if (evt.keyCode==13)
					plugins.search.performSearch.call(evt.data.datatable, $(this).val());
			},
			searchSubmit : function(evt)
			{
				if( typeof evt.data.datatable == 'undefined' ) {
					return false;
				}
				evt.keyCode = 13;
				evt.type = 'keyup';
				evt.data.searchbox.trigger(evt).focus();
			},
			searchReset : function(evt)
			{
				if( typeof evt.data.datatable == 'undefined' ) {
					return false;
				}
				evt.data.searchbox.val('');
				delete _requestData.search;
				$(evt.data.datatable).datatable().refresh();
			},
			performSearch : function(str)
			{
				_requestData.search = str;
				$(this).datatable().refresh();
			}
		},
		header :
		{
			init : function()
			{
				if( options.headerTemplate )
					$(this).find('thead').html( $.tmpl($('#'+options.headerTemplate), {}) );
				// set header objects functionallity
				plugins.header._init.call(this);
			},
			/**
			 * set the header
			 *
			 * this = datatable object
			 */
			_init : function()
			{
				var thisObj = this; // datatable
				// bind header columns actions
				$(this).find('thead th').each( function()
				{
					// breaks sort functionallity
					if ($(this).hasClass('unsortable'))
						return true;

					var thisX = this;
					// set filter functionallity
					if ($(this).hasClass('filterable'))
					{
						// hide, bind close event for filter box
						$(this).find('input').hide().bind( 'hide-filter', {'datatable': thisObj}, function(evt)
						{
							plugins.header.closeFilter.call(thisX, evt);
						});

						// bind close filter to hide control
						$(this).find('.filter-hide-ctrl')
							.hide()
							.bind( 'click', function(evt)
							{
								evt.stopImmediatePropagation();
								$(thisX).find('input').trigger('hide-filter');
							});

						$(this).find('.filter-ctrl').hide();
						$(this).delegate( 'a.sort-ctrl', 'click', {'datatable': thisObj},
							function(evt){ plugins.header.performSort.call(thisX, evt); } );
						$(this).bind( 'click', {'datatable': thisObj}, plugins.header.initFilter );
					}
					else {
						$(this).bind( 'click', {'datatable': thisObj},
							function(evt){ plugins.header.performSort.call(thisX, evt); } );
					}
				});
				$(thisObj).trigger('datatable-setheader');
			},
			/**
			 * provides sorting functionallity per column
			 */
			performSort : function(evt)
			{
				if( typeof evt.data.datatable == 'undefined' )
					return false;

				var siblings = $(this).parent('tr').find('td');
				_requestData['sort-idx'] = siblings.index($(this));
				_requestData['sort'] = $(this).attr('sort') ? $(this).attr('sort') : _requestData['sort-idx'];

				if (!$(this).data('datatable-sort-dir')) {
					$(this).data('datatable-sort-dir','desc');
				}
				if ($(this).hasClass('desc')) {
					$(this).data('datatable-sort-dir','asc');
					siblings.removeClass('desc').removeClass('asc');
					$(this).removeClass('desc').addClass('asc');
				}
				else {
					$(this).data('datatable-sort-dir', 'desc');
					siblings.removeClass('desc').removeClass('asc');
					$(this).removeClass('asc').addClass('desc');
				}

				_requestData['sort-dir'] = $(this).data('datatable-sort-dir');
				dataRequest.call(evt.data.datatable);

				$(evt.data.datatable).trigger('datatable-sorting');
				evt.stopImmediatePropagation();
			},
			initFilter : function(evt)
			{
				if( typeof evt.data.datatable == 'undefined' ) {
					return false;
				}
				var thisX = this;
				$(this).find('label').hide();
				$(this).find('.filter-hide-ctrl').show();

				var filterInput = $(this).find('input').show().focus()
					.bind( 'keyup.datatable', evt.data,  function(evt) { plugins.header.performFilter.call(thisX, evt); } );

				$(this).find('.filter-ctrl').show()
					// simulate keyup on filter ctrl click
					.bind( 'click.datatable', evt.data,
						function(evt)
						{
							evt.keyCode = 13;
							evt.type = 'keyup';
							filterInput.trigger(evt).focus();
						});

				$(this).trigger('datatable-filter-open');
			},
			/**
			 * perform the actual filter
			 *
			 * this = header td
			 */
			performFilter : function(evt)
			{
				if( typeof evt.data.datatable == 'undefined' ) return false;

				// hide on escape key
				if( evt.keyCode==27 )
				{
					plugins.header.closeFilter.call(this, evt);
					return;
				}
				// return on empty value
				if( $.trim($(this).find('input').val())=='' ) return false;

				// perform filter
				if( evt.keyCode==13 )
				{
					var siblings = $(this).parent('tr').find('td');
					_requestData['filter'] = $(this).attr('filter') ? $(this).attr('filter') : siblings.index($(this));
					_requestData['filter-value'] = $(this).find('input').val();
					dataRequest.call(evt.data.datatable);
				}
				$(this).trigger('datatable-filtering');
				evt.stopImmediatePropagation();
			},
			/**
			 * close column filter
			 */
			closeFilter : function(evt)
			{
				if( typeof evt.data.datatable == 'undefined' ) return false;

				$(this).find('label').show();
				$(this).find('.filter-hide-ctrl').hide();
				$(this).find('.filter-ctrl').hide();
				$(this).find('input').val('').hide().unbind( 'keyup.datatable' );

				delete _requestData['filter'];
				delete _requestData['filter-value'];
				dataRequest.call(evt.data.datatable);

				$(this).trigger('datatable-filter-closed');
			}
		},
		footer :
		{
			init : function()
			{
				if( plugins.footer.setPagination )
					plugins.footer.setPagination.call(this);
			},
			setPagination : function()
			{
				var self = this;
				$(self).bind( 'datatable-data-success', function(event, response)
				{
					// make pagination
					if( typeof response.pagination != 'undefined' )
					{
						var footerBox = $(self).find('tfoot');
						footerBox.tmpl
						(
							$('#'+options.footerTemplate), $.extend( {}, { 'data' : response.data }, response.pagination )
						);
						$(self).find('tfoot tr td').attr( 'colspan', $(self).find('thead tr td').length );
					}
				});
				$(self).find('tfoot a').live( 'click', function(evt)
				{
					var params = $(this).attr('href').split("/");
					for( var i = 0; i < params.length; i++ )
						_requestData[params[i]] = params[++i];

					$(self).datatable().refresh();
					evt.preventDefault();
				});
			}
		}
	};

	// initialize
	if( !(typeof options === 'string') )
	{
		var options = $.extend( {}, defaults, options );
		var plugins = $.extend( {}, plugins, userPlugins );
	}

	// get 1 specific object's datatable properties and methods after init
	var args = arguments;
	if( args.length == 0 )
	{
		if( typeof $(this).get(0)['_datatable'] == 'undefined' )
		{
			if( typeof console != 'undefined' )
				console.error('Please initialize the datatable first with some options');
			return false;
		}
		return $(this).get(0)['_datatable'];
	}

	return this.each( function()
	{
		// init plugins
		for( i in plugins )
			if( plugins[i] && typeof plugins[i].init == 'function' )
				plugins[i].init.call(this);

		// create an object property specifically for the datatable
		var self = this;
		mergeObj =
		{
			_datatable : // with _ so we don't conflict anything with the function name..
			{
				plugins : plugins,
				options : options,
				
                refresh : function()
				{                       
					dataRequest.call(self);
				},
				// extend current plugin list
				addPlugin : function( name, plugin )
				{
					if( typeof name == 'object' )
						var newPlugin = name;
					else
					{
						var newPlugin = {};
						newPlugin[name] = plugin;
					}
					$.extend( this.plugins, newPlugin );
					if( typeof newPlugin.init == 'function' )
						newPlugin.init.call(self);
					return self;
				},		
				// extend current options list
				addOption : function( name, option )
				{
					if( typeof name == 'object' )
						var newOptions = name;
					else
					{
						var newOptions = {};
						newOptions[name] = option;
					}
					$.extend( this.options, newOptions );
					return self;
				},
                setVector: function( name, value)
                {
                    if( $.isArray(_requestVector[name])) {
                        if($.inArray(value, _requestVector[name]) == -1) {
                            _requestVector[name].push(value);
                        }
                    } else {
                        _requestVector[name] = [value];
                    }
                    return self._datatable;
                },
                removeVector: function( name, value)
                {
                    if( $.isArray(_requestVector[name])) {
                        if((pos = $.inArray(value, _requestVector[name])) != -1) {
                            _requestVector[name].splice(pos,1);
                        }
                    }
                    return self._datatable;
                },
				setParam : function( name, value )
				{
					_requestData[name] = value;
					return self._datatable;
				},                
				removeParam : function( name )
				{
					delete _requestData[name];
					return self._datatable;
				},
                getData: function()
                {
                    return _requestData;
                },
                end: function()
                {
                    return self;
                }
			}
		};
		$.extend(this, mergeObj);

		// initial data call
		this._datatable.refresh();
		$(this).trigger('datatable-init');
	});
};



(function( $, undefined )
{
	$.widget( "ui.datatable", 
	{
		plugins : 
		{
	       loader : 
	       {
	            init: function()
	            {
	                plugins.loader._init.call(this);
	            },
	            _init : function()
	            {
	                $(this).bind('datatable-init',function(){
	                    if( options.loaderTemplate ) {
	                        $(this).prepend($.tmpl($('#'+options.loaderTemplate), {}));
	                    }
	                })
	                .bind('datatable-data-success',function(){
	                    plugins.loader.toggleOverlay.call(this, false);
	                })
	                .bind('datatable-data-close',function(){
	                    plugins.loader.toggleOverlay.call(this, false);
	                })
	                .bind('datatable-data-refresh',function(){
	                    plugins.loader.toggleOverlay.call(this, true);
	                });
	            },
	            toggleOverlay: function(sw){                                
					$(this).find('.loading-message:first').html($(this).data('loading-message'));
					if(sw) {
	                    $(this).find('.loading-overlay').show();
	                }
	                else
	                    $(this).find('.loading-overlay').hide();
	            },
				addMessage: function(msg){
						console.log(msg,msg.length);
						msgBox = $(this).find('.loading-message');
						if(!msgBox.length) {
							msgBox = $('<div class="loading-message"></div>');
							aux = $(this).find('.loading-overlay');
							aux.append(msgBox);
						}
						msgBox.html(msg);
				}
	        },
			search :
			{
				init : function()
				{
					plugins.search._init.call(this);
				},
				_init : function()
				{
					var searchbox = $(this).find('.header .search input[type=text]');
					var searchsubmit = $(this).find('.header .search input[type=submit]');
					var searchreset = $(this).find('.header .search input[type=reset]');

					searchbox.bind( 'keyup.datatable', { 'datatable': this }, plugins.search.searchboxKeyup );
					searchsubmit.bind( 'click.datatable', { 'datatable' : this, 'searchbox' : searchbox }, plugins.search.searchSubmit );
					searchreset.bind( 'click.datatable', { 'datatable' : this, 'searchbox' : searchbox }, plugins.search.searchReset );
				},
				searchboxKeyup : function(evt)
				{
					if( typeof evt.data.datatable == 'undefined' ) {
						return false;
					}

					// return on empty value
					if( $.trim($(this).val()) == '' ) return false;

					if (evt.keyCode==13)
						plugins.search.performSearch.call(evt.data.datatable, $(this).val());
				},
				searchSubmit : function(evt)
				{
					if( typeof evt.data.datatable == 'undefined' ) {
						return false;
					}
					evt.keyCode = 13;
					evt.type = 'keyup';
					evt.data.searchbox.trigger(evt).focus();
				},
				searchReset : function(evt)
				{
					if( typeof evt.data.datatable == 'undefined' ) {
						return false;
					}
					evt.data.searchbox.val('');
					delete _requestData.search;
					$(evt.data.datatable).datatable().refresh();
				},
				performSearch : function(str)
				{
					_requestData.search = str;
					$(this).datatable().refresh();
				}
			},
			header :
			{
				_create: function() 
				{
					if( options.headerTemplate )
						$(this).find('thead').html( $.tmpl($('#'+options.headerTemplate), {}) );

					var thisObj = this; // datatable
					// bind header columns actions
					$(this).find('thead th').each( function()
					{
						// breaks sort functionallity
						if ($(this).hasClass('unsortable'))
							return true;

						var thisX = this;
						// set filter functionallity
						if ($(this).hasClass('filterable'))
						{
							// hide, bind close event for filter box
							$(this).find('input').hide().bind( 'hide-filter', {'datatable': thisObj}, function(evt)
							{
								plugins.header.closeFilter.call(thisX, evt);
							});

							// bind close filter to hide control
							$(this).find('.filter-hide-ctrl')
								.hide()
								.bind( 'click', function(evt)
								{
									evt.stopImmediatePropagation();
									$(thisX).find('input').trigger('hide-filter');
								});

							$(this).find('.filter-ctrl').hide();
							$(this).delegate( 'a.sort-ctrl', 'click', {'datatable': thisObj},
								function(evt){ plugins.header.performSort.call(thisX, evt); } );
							$(this).bind( 'click', {'datatable': thisObj}, plugins.header.initFilter );
						}
						else {
							$(this).bind( 'click', {'datatable': thisObj},
								function(evt){ plugins.header.performSort.call(thisX, evt); } );
						}
					});
					$(thisObj).trigger('datatable-setheader');
				},
				/**
				 * provides sorting functionallity per column
				 */
				performSort : function(evt)
				{
					if( typeof evt.data.datatable == 'undefined' )
						return false;

					var siblings = $(this).parent('tr').find('td');
					_requestData['sort-idx'] = siblings.index($(this));
					_requestData['sort'] = $(this).attr('sort') ? $(this).attr('sort') : _requestData['sort-idx'];

					if (!$(this).data('datatable-sort-dir')) {
						$(this).data('datatable-sort-dir','desc');
					}
					if ($(this).hasClass('desc')) {
						$(this).data('datatable-sort-dir','asc');
						siblings.removeClass('desc').removeClass('asc');
						$(this).removeClass('desc').addClass('asc');
					}
					else {
						$(this).data('datatable-sort-dir', 'desc');
						siblings.removeClass('desc').removeClass('asc');
						$(this).removeClass('asc').addClass('desc');
					}

					_requestData['sort-dir'] = $(this).data('datatable-sort-dir');
					dataRequest.call(evt.data.datatable);

					$(evt.data.datatable).trigger('datatable-sorting');
					evt.stopImmediatePropagation();
				},
				initFilter : function(evt)
				{
					if( typeof evt.data.datatable == 'undefined' ) {
						return false;
					}
					var thisX = this;
					$(this).find('label').hide();
					$(this).find('.filter-hide-ctrl').show();

					var filterInput = $(this).find('input').show().focus()
						.bind( 'keyup.datatable', evt.data,  function(evt) { plugins.header.performFilter.call(thisX, evt); } );

					$(this).find('.filter-ctrl').show()
						// simulate keyup on filter ctrl click
						.bind( 'click.datatable', evt.data,
							function(evt)
							{
								evt.keyCode = 13;
								evt.type = 'keyup';
								filterInput.trigger(evt).focus();
							});

					$(this).trigger('datatable-filter-open');
				},
				/**
				 * perform the actual filter
				 *
				 * this = header td
				 */
				performFilter : function(evt)
				{
					if( typeof evt.data.datatable == 'undefined' ) return false;

					// hide on escape key
					if( evt.keyCode==27 )
					{
						plugins.header.closeFilter.call(this, evt);
						return;
					}
					// return on empty value
					if( $.trim($(this).find('input').val())=='' ) return false;

					// perform filter
					if( evt.keyCode==13 )
					{
						var siblings = $(this).parent('tr').find('td');
						_requestData['filter'] = $(this).attr('filter') ? $(this).attr('filter') : siblings.index($(this));
						_requestData['filter-value'] = $(this).find('input').val();
						dataRequest.call(evt.data.datatable);
					}
					$(this).trigger('datatable-filtering');
					evt.stopImmediatePropagation();
				},
				/**
				 * close column filter
				 */
				closeFilter : function(evt)
				{
					if( typeof evt.data.datatable == 'undefined' ) return false;

					$(this).find('label').show();
					$(this).find('.filter-hide-ctrl').hide();
					$(this).find('.filter-ctrl').hide();
					$(this).find('input').val('').hide().unbind( 'keyup.datatable' );

					delete _requestData['filter'];
					delete _requestData['filter-value'];
					dataRequest.call(evt.data.datatable);

					$(this).trigger('datatable-filter-closed');
				}
			},
			footer :
			{
				init : function()
				{
					if( plugins.footer.setPagination )
						plugins.footer.setPagination.call(this);
				},
				setPagination : function()
				{
					var self = this;
					$(self).bind( 'datatable-data-success', function(event, response)
					{
						// make pagination
						if( typeof response.pagination != 'undefined' )
						{
							var footerBox = $(self).find('tfoot');
							footerBox.tmpl
							(
								$('#'+options.footerTemplate), $.extend( {}, { 'data' : response.data }, response.pagination )
							);
							$(self).find('tfoot tr td').attr( 'colspan', $(self).find('thead tr td').length );
						}
					});
					$(self).find('tfoot a').live( 'click', function(evt)
					{
						var params = $(this).attr('href').split("/");
						for( var i = 0; i < params.length; i++ )
							_requestData[params[i]] = params[++i];

						$(self).datatable().refresh();
						evt.preventDefault();
					});
				}
			}
		},
		options: 
		{
			
		},
		_create : function()
		{
			//$(this.element).attr('contentEditable', true);
		},
		_init: function() 
		{ 
			
		},
		_setOption: function( key, value ) 
		{
			//$.Widget.prototype._setOption.apply( this, arguments );
		},
		_destroy: function() 
		{ 
			
		}
	});	
})(jQuery);