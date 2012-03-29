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
				},
				createRequest: function()
				{
					var self = this._self;
					if(typeof self.options.resource == 'string')
						this._request = new $.rest(self.options.resource);
					else
						this._request = self.options.resource;
					
					return this;
				},
				executeRequest: function()
				{
					var self = this._self;
					if(this._request)
						return this._request.done(function(data)
						{
							self.plugins.body.render(data)
						});
				},
				setup: function(settings)
				{
					
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
			header: function()
			{
				this._create = function()
				{
					var self = this; // datatable
					var thead = self.plugins.lib.core.getDatatable().find('thead');
					if(!thead.length) 
					{
						thead = $('<thead />');
						self.plugins.lib.core.getDatatable().append(thead)
					}
					
					if( self.plugins.templates.header )
						thead.tmpl( $(self.plugins.templates.header).wrap('<thead />').parent() );
					
					// bind header columns actions
					thead.find('th').each( function()
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
							$(this).delegate( 'a.sort-ctrl', 'click', {'datatable': self},
								function(evt){ plugins.header.performSort.call(thisX, evt); } );
							$(this).bind( 'click', {'datatable': self}, plugins.header.initFilter );
						}
						else {
							$(this).bind( 'click', {'datatable': self},
								function(evt){ plugins.header.performSort.call(thisX, evt); } );
						}
					});
					
					$(self).trigger('datatable-setheader');
				};
			},
			body: function()
			{
				this._self = null;
				this._create = function()
				{
					this.plugins.body._self = this;
					var tbody = this.plugins.lib.core.getDatatable().find('tbody');
					if( !tbody.length ) 
					{
						tfoot = $('<tbody />');
						this.plugins.lib.core.getDatatable().append(tbody)
					}
				};
				this.render = function(data)
				{
					var self = this._self
					if( self.plugins.templates.body )
						tbody.tmpl( $(this.plugins.templates.body).wrap('<tbody />').parent(), data );
				}
			},
			footer: function()
			{
				this._create = function()
				{
					var tfoot = this.plugins.lib.core.getDatatable().find('tfoot');
					if( !tfoot.length ) 
					{
						tfoot = $('<tfoot />');
						this.plugins.lib.core.getDatatable().append(tfoot)
					}
					if( this.plugins.templates.footer )
						tfoot.tmpl( $(this.plugins.templates.footer).wrap('<tfoot />').parent() );
					
					if( this.plugins.footer.setPagination )
						this.plugins.footer.setPagination.call(this);

				},
				this.setPagination = function()
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

	$('#area-main').html($('<div />').datatable(
	{
		templates: 
		{
			header: '<tr><th>x</th><th>y</th><th>z</th></tr>',
			footer: '<tr><td colspan="3"></td></tr>',
		},
		resource: superdesk.apiUrl + '/resources/Superdesk/User'
	}));
	
	var listPath, updatePath, addPath;
	superdesk.getActions('modules.country.*')
	.done(function(actions)
	{
		$(actions).each(function()
		{  
			switch(this.Path)
			{
				case 'modules.counrty.list': listPath = this.scriptPath; break;
				case 'modules.counrty.update': updatePath = this.scriptPath; break;
				case 'modules.counrty.add': addPath = this.scriptPath; break;
			}
		});
		(new superdesk.presentation)
			.setScript(listPath)
			.setLayout(superdesk.layouts.list.clone())
			.setArgs({updateScript: updatePath, addScript: addPath})
			.run();
	});
