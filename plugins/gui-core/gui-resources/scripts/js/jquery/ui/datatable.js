/*!
 * @author Mihai Balaceanu <mihai.balaceanu@sourcefabric.org>
 * @package Superdesk
 * @subpackage Components
 * @copyright 2012 Sourcefabric o.p.s.
 * @license http://www.gnu.org/licenses/gpl.txt
 *
 * @todo maybe add some default templates or escape errors on none found at data request..
 */
define('jqueryui/datatable',['jquery', 'dust', 'jquery/tmpl','jqueryui/widget', 'jqueryui/ext'], function ($,dust) {
    "use strict";
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
                    this.plugins.dataAdapter._self = this;
                    this.plugins.dataAdapter._request = typeof this.options.resource === 'string' ?
                        new $.rest(this.options.resource) :
                        this.options.resource;
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
                            if(this._data.hasOwnProperty(i)) switch(i)
                            {
                                case 'filterDelete':
                                    this._request.resetData(this._data[i]);
                                    break;
                                case 'filterName':
                                    data[this._data[i]] = '%'+this._data.filterValue+'%';
                                    break;
                                case 'sort':
                                    data[this._data.sortDir] = this._data[i];
                                    break;
                            }
                        }
                        
                        this._request.resetData('asc').resetData('desc');
                        $.extend(data, this._data.params);
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
                    if( typeof settings === 'string' ) 
                    {
                        var x = settings;
                        settings = [];
                        settings[x] = true;
                    }
                    
                    for( var i in settings )
                    {
                        if( settings.hasOwnProperty(i) ) switch(i)
                        {
                            case 'params':
                                $.extend(this._data.params, settings[i]);
                                break;
                            case 'removeFilter':
                                this._data.filterDelete = this._data.filterName;
                                delete this._data.filterName;
                                delete this._data.filterValue;
                                break;
                            case 'filter':
                                this._data.filterName = settings[i].name;
                                this._data.filterValue = settings[i].value;
                                break;
                            case 'sort':
                                this._data.sort = settings[i].sort;
                                this._data.sortDir = settings[i].sortDir;
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
                        if( !this._element ) this._element = $('<table />');
                        return this._element;
                    },
                    replaceDatatable: function(elem)
                    {
                        elem.append(this.getDatatable().contents());
                        this._element = elem;
                    }
                }
            },
            other: 
            {
                _create: function()
                { 
                    if( typeof this.options.tpl === 'object' ) 
                        $.extend(true, this.options.templates, this.options.tpl);
                }  
            },
            header: 
            {
                _create: function()
                {
                    var self = this; // datatable
                    if( !self.options.templates.header ) return;
					$.tmpl(self.options.templates.header, {}, function(err, out) 
                    {
                        self.plugins.header._display.call(self, out);
                    });
                },
                _display: function(html)
                {
                    var head = $(html),
                        self = this;
                    
                    self.plugins.lib.core.getDatatable().append(head);
                    // bind header columns actions
                    head.find(self.options.headerColumnSelector).each( function()
                    {
                        // breaks sort functionality
                        if ($(this).hasClass('unsortable') || typeof $(this).attr('unsortable') !== 'undefined') return true;

                        var thisX = this;
                        // set filter functionality
                        if ($(this).hasClass('filterable') || typeof $(this).attr('filterable') !== 'undefined')
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
                    // add class for cell filtering
                    $(this).addClass(evt.data.datatable.options.filterCellClass);
                    
                    $(this).find('label').hide();
                    $(this).find('.filter-hide-ctrl').css({display: 'inline-block'});

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

                    $(this).removeClass(evt.data.datatable.options.filterCellClass);
                    
                    $(this).find('label').show();
                    $(this).find('.filter-hide-ctrl').hide();
                    $(this).find('.filter-ctrl').hide();
                    $(this).find('input').val('').hide().unbind( 'keyup.datatable' );

                    evt.data.datatable.plugins.dataAdapter.setup('removeFilter').executeRequest();
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
                    if( evt.keyCode === 27 )
                    {
                        evt.data.datatable.plugins.header.closeFilter.call(this, evt);
                        return;
                    }
                    // return on empty value
                    if( $.trim($(this).find('input').val())=='' ) return false;

                    // perform filter
                    if( evt.keyCode === 13 )
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
                    if( typeof evt.data.datatable === 'undefined' )
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
                _template: null,
                _element: null,
                getElement: function()
                {
                    if(!this._element)
                        this._element = $('<tbody />');
                    return this._element;
                },
                _create: function()
                {
                    if( !this.options.templates.body ) return false;

                    this.plugins.lib.core.getDatatable().append(this.plugins.body.getElement());
                    $(this).on('data-request-success.datatable', function(event, data)
                    {
                        this.plugins.body.render.call(this, data);
                    });
                },
                /*!
                 * this = plugin - this.plugins.body.render.apply(this, [...])
                 */
                render: function(data)
                {
                    var self = this;                   
                    // TODO error mechanism
					$.tmpl(this.options.templates.body, {data: data}, function(error, output)
                    {
                        var newBody = $(output);
                        self.plugins.body._element.replaceWith(newBody);
                        self.plugins.body._element = newBody;
                    });
                    //var newBody = $($.tmpl( this.options.templates.body, {data: data} ));
                    //$(this.plugins.body._element).replaceWith(newBody);
                    //this.plugins.body._element = newBody;
                }
            },
            footer: 
            {
                _template: null,
                _element: null,
                getElement: function()
                {
                    if(!this._element)
                        this._element = $('<tfoot />');
                    return this._element;
                },
                _create: function()
                {
                    if( !this.options.templates.footer ) return;                        
                    this.plugins.lib.core.getDatatable().append(this.plugins.footer.getElement());
                    
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

                            self.plugins.footer._args.offset = parseInt(_requestData.offset);
                            self.plugins.dataAdapter.setup({ params: _requestData }).executeRequest();
                            evt.preventDefault();
                        };
                    
                    $(this).one( 'data-request-success.datatable', function(event, response)
                    {
                        this.plugins.footer._args.limit = parseInt(response.length);
                    });
                        
                    $(this).on( 'data-request-success.datatable', function(event, response)
                    {
                        // make pagination
                        if( typeof response === 'undefined' ) return;
                        
                        var _args = this.plugins.footer._args,
                            args = this.plugins.dataAdapter.getRequest().responseArgs();

                        var nextCheck = parseInt(_args.offset) + parseInt(_args.limit),
                            prevCheck = parseInt(_args.offset) - parseInt(_args.limit);
                        
                        _args.next = nextCheck <= args.total ? nextCheck : _args.offset;
                        _args.prev = prevCheck >= 0 ? prevCheck : 0;
                        
                        var paginationObject = { pagination: 
                        { 
                            total: args.total, 
                            offset: _args.offset, 
                            limit: _args.limit,
                            range: _args.offset + _args.limit,
                            next: 'offset/' + _args.next, 
                            prev: 'offset/' + _args.prev,
                            prevElement: this.options.templateMarks.prevAttr+"='1'", 
                            nextElement: this.options.templateMarks.nextAttr+"='1'"
                        }};
                        
                        // TODO error mechanism
                        $.tmpl( this.options.templates.footer, paginationObject, function(error, output)
                        {
                            var newBody = $(output);
                            self.plugins.footer.getElement().replaceWith(newBody);
                            self.plugins.footer._element = newBody;
                            
                            $(self.plugins.footer._element).on("click.datatable", 
                                    '['+self.options.templateMarks.prevAttr+']', prevNextHandler);
                            $(self.plugins.footer._element).on("click.datatable", 
                                    '['+self.options.templateMarks.nextAttr+']', prevNextHandler);
                            
                        });
                    });
                    
                }
            }
        },
        options: 
        {
            filterCellClass: 'filtering',
            headerColumnSelector: 'th',
            templateMarks:
            {
                prevAttr: 'prev-ctrl',
                nextAttr: 'next-ctrl'
            },
            // can also use as "tpl" 
            templates: { header: null, footer: null, body: null }
        },
        _create : function()
        {
            
            if(this.element.is('table'))
                this.plugins.lib.core.replaceDatatable( this.element );
            else
                $(this.element).append(this.plugins.lib.core.getDatatable());
            
            $(this.element).addClass('datatable');
            
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
});