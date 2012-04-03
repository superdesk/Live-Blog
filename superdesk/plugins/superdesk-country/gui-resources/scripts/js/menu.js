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
						return this._request.done(function()
						{
							$(self).trigger('data-request-success.datatable', arguments);
						},
						function()
						{
							$(self).trigger('data-request-error.datatable', arguments);
						});
					return this;
				},
				setup: function(settings)
				{
					for( var i in settings )
					{
						switch(i)
						{
							case 'params':
								this._request.request({data: settings[i]});
								this.executeRequest();
								break;
						}
					}
					return this;
				},
				sort: function(column, dir, index)
				{
					return this.setup('sort', {column: column, dir: dir, index: index});
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
				header: null, footer: null, row: null,
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
					head.find('th').each( function()
					{
						// breaks sort functionality
						if ($(this).hasClass('unsortable'))
							return true;

						var thisX = this;
						// set filter functionality
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
							$(this).delegate( 'a.sort-ctrl', 'click', {'datatable': self},
								function(evt){ plugins.header.performSort.call(thisX, evt); } );
							$(this).bind( 'click', {'datatable': self}, plugins.header.initFilter );
						}
						else 
							$(this).on('click', {'datatable': self}, function(evt)
							{ 
								self.plugins.header.performSort.call(thisX, evt); 
							});
					});
					
					$(self).trigger('set-header.datatable');
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
					evt.data.datatable.plugins.dataAdapter.sort( sort, sortDir, sortIdx ).executeRequest()

					$(evt.data.datatable).trigger('sorting.datatable');
					evt.stopImmediatePropagation();
				}
			},
			body:
			{
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
						console.log(data);
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
				_element: null,
				_create: function()
				{
					if( !this.plugins.templates.footer ) return;
						
					this.plugins.footer._element = $($.tmpl(this.plugins.templates.footer))
					this.plugins.lib.core.getDatatable().append( this.plugins.footer._element );
					
					if( this.plugins.footer.setPagination )
						this.plugins.footer.setPagination.call(this);

				},
				/*!
				 * this = plugin - this.plugins.body.render.apply(this, [...])
				 */
				setPagination: function()
				{
					var self = this,
						offset = 0,
						limit = 10,
						next, prev,
						
						prevNextHandler = function(evt)
						{
							var params = $(this).attr('href').split("/"), 
								_requestData = {};
							for( var i = 0; i < params.length; i++ )
								_requestData[params[i]] = params[++i];

							self.plugins.dataAdapter.setup({ params: _requestData }).executeRequest();
							evt.preventDefault();
						};
						
					$(this).bind( 'data-request-success.datatable', function(event, response)
					{
						// make pagination
						if( typeof response == 'undefined' ) return;
						
						var args = this.plugins.dataAdapter.getRequest().responseArgs()
						next = offset + limit <= args.total ? offset + limit : offset;
						prev = offset - limit >= 0 ? offset - limit : 0;
						var paginationObject = { pagination: 
						{ 
							total: args.total, offset: offset, limit: limit, next: 'offset/'+next, prev: 'offset/'+prev,
							prevElement: "prev-ctrl='1'", nextElement: "next-ctrl='1'"
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
