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
(function( $, undefined )
{
	$.widget( "ui.datatable", 
	{
		plugins : 
		{
			dataAdapter: 
			{
				_self: null,
				_request: null,
				_create: function()
				{
					this.plugins.dataAdapter._self = this
					if(typeof this.options.resource == 'string')
						this.plugins.dataAdapter._request = new $.rest(this.options.resource);
					else
						this.plugins.dataAdapter._request = this.options.resource;
					this.plugins.dataAdapter._request.keepXFilter = true;
				},
				createRequest: function()
				{
					return this;
				},
				getRequest: function()
				{
					return this._request;
				},
				executeRequest: function()
				{
					var self = this._self;
					if(this._request)
					{
						var data = {};
						for( var i in this._data )
						{
							switch(i)
							{
								case 'filter-name':
									data[this._data[i]] = this._data['filter-value'];
									break;
								case 'sort':
									data[this._data['sort-dir']] = this._data[i];
									break;
							}
						};
						this._request.resetData('asc').resetData('desc');
						$.extend(data, this._data['params']);
						this._request.request({data: data});
						
						return this._request.done(function()
						{
							$(self).trigger('data-request-success.datatable', arguments);
						},
						function()
						{
							$(self).trigger('data-request-error.datatable', arguments);
						});
					}
					return this;
				},
				_data: {params: {}},
				setup: function(settings)
				{
					if( typeof settings == 'string' ) settings = [settings];
					for( var i in settings )
					{
						switch(i)
						{
							case 'params':
								$.extend(this._data['params'], settings[i]);
								break;
							case 'filter':
								this._data['filter-name'] = settings[i].name;
								this._data['filter-value'] = settings[i].value;
								break;
							case 'sort':
								this._data['sort'] = settings[i].sort;
								this._data['sort-dir'] = settings[i].sortDir;
								break;
						}
					}
					return this;
				}
			},
			lib:
			{
				core: 
				{
					_element: null,
					getDatatable: function()
					{
						if( !this._element ) this._element = $('<table />')
						return this._element;
					}
				}
			},
			templates:
			{
				_create: function()
				{
					var optTpl = this.options.templates || this.options.tpl;
					if( !optTpl ) return;
					for( var i in optTpl )
						this.plugins.templates[i] = optTpl[i];
				},
				header: null, footer: null, row: null
			},
			header: 
			{
				_create: function()
				{
					var self = this; // datatable
					if( !self.plugins.templates.header ) return;

					var head = $($.tmpl(self.plugins.templates.header))
					self.plugins.lib.core.getDatatable().append(head);
					
					// bind header columns actions
					// TODO fix th lookup
					head.find('th').each( function()
					{
						// breaks sort functionality
						if ($(this).hasClass('unsortable') || typeof $(this).attr('unsortable') != 'undefined') return true;

						var thisX = this;
						// set filter functionality
						if ($(this).hasClass('filterable') || typeof $(this).attr('filterable') != 'undefined')
						{
							// hide, bind close event for filter box
							$(this).find('input').hide().on( 'hide-filter.datatable', {'datatable': self}, function(evt)
							{
								self.plugins.header.closeFilter.call(thisX, evt);
							});

							// bind close filter to hide control
							$(this).find('.filter-hide-ctrl')
								.hide()
								.on( 'click', function(evt)
								{
									evt.stopImmediatePropagation();
									$(thisX).find('input').trigger('hide-filter.datatable');
								});

							$(this).find('.filter-ctrl').hide();
							$(this).on( 'click', 'a.sort-ctrl', {'datatable': self},
								function(evt){ self.plugins.header.performSort.call(thisX, evt); } );
							$(this).on( 'click', {'datatable': self}, self.plugins.header.initFilter );
						}
						else
						{
							$(this).on('click', {'datatable': self}, function(evt)
							{ 
								self.plugins.header.performSort.call(thisX, evt); 
							});
						}
					});
					
					$(self).trigger('set-header.datatable');
				},
				/*!
				 * show filter interface
				 */
				initFilter : function(evt)
				{
					if( typeof evt.data.datatable == 'undefined' ) 
						return false;
					
					var thisX = this;
					$(this).find('label').hide();
					$(this).find('.filter-hide-ctrl').show();

					var filterInput = $(this).find('input').show().focus()
						.on( 'keyup.datatable', evt.data,  function(evt) 
						{ 
							evt.data.datatable.plugins.header.performFilter.call(thisX, evt); 
						});

					$(this).find('.filter-ctrl').show()
						// simulate keyup on filter ctrl click
						.bind( 'click.datatable', evt.data,
							function(evt)
							{
								evt.keyCode = 13;
								evt.type = 'keyup';
								filterInput.trigger(evt).focus();
							});

					$(this).trigger('filter-open.datatable');
				},
				/*!
				 * close column filter
				 */
				closeFilter : function(evt)
				{
					if( typeof evt.data.datatable == 'undefined' ) return false;

					$(this).find('label').show();
					$(this).find('.filter-hide-ctrl').hide();
					$(this).find('.filter-ctrl').hide();
					$(this).find('input').val('').hide().unbind( 'keyup.datatable' );

					evt.data.datatable.plugins.dataAdapter.setup('remove-filter').executeRequest();
					$(this).trigger('filter-closed.datatable');
				},
				/*!
				 * perform the actual filter
				 *
				 * this = header dom elem
				 */
				performFilter : function(evt)
				{
					if( typeof evt.data.datatable == 'undefined' ) return false;

					// hide on escape key
					if( evt.keyCode==27 )
					{
						evt.data.datatable.plugins.header.closeFilter.call(this, evt);
						return;
					}
					// return on empty value
					if( $.trim($(this).find('input').val())=='' ) return false;

					// perform filter
					if( evt.keyCode==13 )
					{
						evt.data.datatable.plugins.dataAdapter
							.setup({filter: {name: $(this).attr('filter'), value: $(this).find('input').val()}})
							.executeRequest();
					}
					$(this).trigger('filtering.datatable');
					evt.stopImmediatePropagation();
				},
				/*!
				 * provides sorting functionality per column
				 */
				performSort : function(evt)
				{
					if( typeof evt.data.datatable == 'undefined' )
						return false;

					var sortIdx = $(this).siblings().andSelf().index(this), 
						sort = $(this).attr('sort') ? $(this).attr('sort') : sortIdx;

					if (!$(this).data('datatable-sort-dir')) 
						$(this).data('datatable-sort-dir','desc');
					
					if ($(this).hasClass('desc'))
					{
						$(this).data('datatable-sort-dir','asc');
						$(this).siblings().removeClass('desc').removeClass('asc');
						$(this).removeClass('desc').addClass('asc');
					}
					else 
					{
						$(this).data('datatable-sort-dir', 'desc');
						$(this).siblings().removeClass('desc').removeClass('asc');
						$(this).removeClass('asc').addClass('desc');
					}

					var sortDir = $(this).data('datatable-sort-dir');
					evt.data.datatable.plugins.dataAdapter
						.setup({ sort: {sort: sort, sortDir: sortDir, sortIdx: sortIdx} }).executeRequest();

					$(evt.data.datatable).trigger('sorting.datatable');
					evt.stopImmediatePropagation();
				}
			},
			body:
			{
				// dom element
				_element: null,
				_create: function()
				{
					if( this.plugins.templates.body )
					{
						this.plugins.body._element = $($.tmpl(this.plugins.templates.body, {data: {}}));
						this.plugins.lib.core.getDatatable().append( this.plugins.body._element );
					}
					
					$(this).on('data-request-success.datatable', function(event, data)
					{
						this.plugins.body.render.call(this, data)
					})
				},
				/*!
				 * this = plugin - this.plugins.body.render.apply(this, [...])
				 */
				render: function(data)
				{
					var newBody = $($.tmpl( this.plugins.templates.body, {data: data} ));
					$(this.plugins.body._element).replaceWith(newBody);
					this.plugins.body._element = newBody;
				}
			},
			footer: 
			{
				// dom obj
				_element: null,
				_create: function()
				{
					if( !this.plugins.templates.footer ) return;
						
					this.plugins.footer._element = $($.tmpl(this.plugins.templates.footer))
					this.plugins.lib.core.getDatatable().append( this.plugins.footer._element );
					
					if( this.plugins.footer.setPagination )
						this.plugins.footer.setPagination.call(this);

				},
				_args: { offset: 0, limit: null, next: null, prev: null },
				/*!
				 * this = plugin - this.plugins.body.render.apply(this, [...])
				 */
				setPagination: function()
				{
					var self = this,
						prevNextHandler = function(evt)
						{
							var params = $(this).attr('href').split("/"), 
								_requestData = {};
							for( var i = 0; i < params.length; i++ )
								_requestData[params[i]] = params[++i];

							self.plugins.footer._args.offset = _requestData.offset;
							self.plugins.dataAdapter.setup({ params: _requestData }).executeRequest();
							evt.preventDefault();
						};
					
					$(this).one( 'data-request-success.datatable', function(event, response)
					{
						this.plugins.footer._args.limit = response.length;
					});
						
					$(this).on( 'data-request-success.datatable', function(event, response)
					{
						// make pagination
						if( typeof response == 'undefined' ) return;
						
						var _args = this.plugins.footer._args,
							args = this.plugins.dataAdapter.getRequest().responseArgs();

						var	nextCheck = parseInt(_args.offset) + parseInt(_args.limit),
							prevCheck = parseInt(_args.offset) - parseInt(_args.limit);
						
						_args.next = nextCheck <= args.total ? nextCheck : _args.offset;
						_args.prev = prevCheck >= 0 ? prevCheck : 0;
						
						var paginationObject = { pagination: 
						{ 
							total: args.total, 
							offset: _args.offset, 
							limit: _args.limit, 
							next: 'offset/' + _args.next, 
							prev: 'offset/' + _args.prev,
							prevElement: "prev-ctrl='1'", 
							nextElement: "next-ctrl='1'"
						}};
						
						var newFooter = $($.tmpl( this.plugins.templates.footer, paginationObject ));
						$(this.plugins.footer._element).replaceWith(newFooter);
						this.plugins.footer._element = newFooter;
						
						$(this.plugins.footer._element).on("click.datatable", "[prev-ctrl]", prevNextHandler);
						$(this.plugins.footer._element).on("click.datatable", "[next-ctrl]", prevNextHandler);
						
					});
					
				}
			}
		},
		options: 
		{
			
		},
		_create : function()
		{
			if(this.element.is('table'))
				$(this.element).append(this.plugins.lib.core.getDatatable().contents())
			else
				$(this.element).append(this.plugins.lib.core.getDatatable());
			this.plugins.dataAdapter.createRequest().executeRequest();
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

//-----


	var listPath, updatePath, addPath;
	superdesk.getActions('modules.country.*')
	.done(function(actions)
	{
		$(actions).each(function()
		{  
			switch(this.Path)
			{
				case 'modules.country.list': listPath = this.ScriptPath; break;
				case 'modules.country.update': updatePath = this.ScriptPath; break;
				case 'modules.country.add': addPath = this.ScriptPath; break;
			}
		});

		(new superdesk.presentation)
			.setScript(listPath)
			.setLayout(superdesk.layouts.list.clone())
			.setArgs({updateScript: updatePath, addScript: addPath})
			.run();
	});
