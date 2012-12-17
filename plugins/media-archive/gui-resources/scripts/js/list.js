requirejs.config
({
    paths: 
    { 
        'media-types': config.gui('media-archive/scripts/js/types')
    }
});
define
([
    'jquery',
    'jquery/superdesk',
    'gizmo/superdesk',
    'gizmo/views/list',
    'utils/nlp',
    config.guiJs('media-archive', 'models/meta-data'),
    config.guiJs('media-archive', 'models/meta-type'),
    config.guiJs('media-archive', 'models/meta-data-info'),
    config.guiJs('media-archive', 'models/query-criteria'),
    config.guiJs('media-archive', 'add'),
    'tmpl!media-archive>list',
    'tmpl!media-archive>sidebar/types',
    'tmpl!media-archive>sidebar/crit-date',
    'tmpl!media-archive>sidebar/crit-numeric',
    'tmpl!media-archive>sidebar/crit-string',
],
function($, superdesk, giz, gizList, nlp, MetaData, MetaType, MetaDataInfo, QueryCriteria, Add)
{
    var // collections
    MetaDataCollection = giz.Collection.extend({ model: MetaData, href: MetaData.prototype.url.get() }),
    MetaTypeCollection = giz.Collection.extend({ model: MetaType, href: MetaType.prototype.url.get() }),
    MetaDataInfos = giz.Collection.extend({ model: MetaDataInfo, href: MetaDataInfo.prototype.url.get() }),
    QueryCriteriaList = giz.Collection.extend({ model: QueryCriteria, href: QueryCriteria.prototype.url.get() }),
    // ---
      
    aintersect = function(a1, a2)
    {
        var results = [], lookup = {}, i;
        for( i = 0; i < a1.length; i++ ) lookup[a1[i]] = true;
        for( i = 0; i < a2.length; i++ ) if( a2[i] in lookup ) results.push(a2[i]);
        
        return results;
    }
    /*!
     * @see gizmo/views/list/ItemView
     */
    ItemView = gizList.ItemView.extend
    ({
        model: null,
        tagName: 'div',
        tmpl: 'media-archive>item',
        render: function()
        {
            require(['media-types/'+this.model.get('Type')+'/grid-view']);
            $(this.el).tmpl(this.tmpl, {Item: this.model.feed()});
            $(this.el).prop('model', this.model).prop('view', this);
            return this;
        },
        remove: function()
        {
            this.model.remove().sync();
        }
    }),
    
    FilterView = giz.View.extend
    ({
        events: 
        {
            "#type-list input": { "click": "selectType" },
            '.open-filter-button': { 'click': 'showFilterList' },
            '#MAFilter': 
            { 
                'keydown': 'key2filter', 
                'keyup': 'keyup2filter' 
            },
            '.filter-list': { 'hover': 'hoverFilterList' },
            '.filter-list li': { 'click': 'selectFilter' },
            '.filters-form': { 'submit': 'saveFilter' },
            '.closebutton': { 'click': 'deleteFilter' }
        },
        tagName: 'span',
        types: null,
        criteriaList: null, 
        init: function()
        {
            this.types = new MetaTypeCollection;
            this.criteriaList = new QueryCriteriaList;
            this.types.on('read update', this.render, this);
            this.criteriaList.on('read update', this.renderCriteria, this);
        },
        placeInView: function(el)
        {
            el.append(this.el);
        },
        /*!
         * refresh types
         */
        refresh: function()
        {
            this.types.xfilter('*').sync();
        },
        render: function()
        {
            var data = this.types.feed(),
                self = this;
            $(this.el).tmpl('media-archive>sidebar/types', {Types: data}, function()
            {
                
                self.criteriaList.sync();
            }); //, PluralType: function(chk, ctx){ console.log(nlp.pluralize(ctx.current().Type)); return 'x' }});
        },

        showFilterList: function()
        {
            if(!$('.filter-list', this.el).hasClass('hide')) $('.filter-list').addClass('hide');
            else $('.filter-list', this.el).removeClass('hide');
            $('#MAFilter', this.el).focus();
        },
        
        criteriaNames: 
        {
            "_any_": _('Any'),
            "qd.videoBitrate": _("Video Bitrate"),
            "qd.videoEncoding": _("Video Encoding"),
            "qd.audioBitrate": _("Audio Bitrate"),
            "qd.audioEncoding": _("Audio Encoding"),
            "qd.sampleRate": _("Sample Rate"),
            "qd.createdOn": _("Date"),
            "qd.fps": _("FPS"),
            "qd.tbpm": _("BPM"),
            "qd.albumArtist": _("Artists"),
            "qd.width": _("Width"),
            "qd.height": _("Height"),
            "qd.genre": _("Genre"),
            "qd.album": _("Album")
        },
        criteriaTypes:
        {
            "AsEqual": "numeric",
            "AsEqualOrdered": "numeric",
            "AsEqualExpression": "numeric",		
            "AsEqualExpressionOrdered": "numeric",
            "AsIn":"string",
            "AsInOrdered": "numeric",
            "AsInExpression": "numeric",		
            "AsInExpressionOrdered": "numeric",	
            "AsLike": "string",
            "AsLikeOrdered": "string",
            "AsLikeExpression": "string",
            "AsLikeExpressionOrdered": "string",
            "AsDateTime": "date",
            "AsDateTimeOrdered": "date",
            "AsDateTimeExpression": "date",
            "AsDateTimeExpressionOrdered": "date"
        },
        /*!
         * @param string criteriaTypes
         * @return string Comparable sorted array for the types on which the criteria applies 
         */
        _criteriaTypes: function(criteriaTypes)
        {
            return criteriaTypes.replace(/InfoEntry-/g,'|').replace(/DataEntry-/g, '|').replace(/\|$/,'').replace(/\|$/,'').toLowerCase().split('|').sort();
        },
        
        

        /*!
         * append filter criteria to select list
         */
        renderCriteria: function()
        {
            var allTypes = [],
                self = this,
                newEntry = '';
            
            // get all types string to compare
            this.types.each(function(){ this.get('Type').toLowerCase() != 'other' && allTypes.push(this.get('Type')); });
            allTypes.sort();
            allTypes = allTypes.toString();
            
            $('#MAFilterResults', self.el).append('<li data-criteria="_any_" data-initial="true">'+_('All')+'</li>');            
            this.criteriaList.each(function()
            {
                var key = this.get('Key');
                if( key in self.criteriaNames ) 
                {
                    newEntry = '<li data-criteria="'+key+'"' ;
                    if( allTypes == self._criteriaTypes(this.get('Types')).toString() )
                    {
                        self._criteriaForAll[key] = true;
                        newEntry += ' data-initial="true"';
                    }
                    newEntry += '>'+self.criteriaNames[key]+'</li>';
                    $('#MAFilterResults', self.el).append(newEntry);
                }
            });
            $('#MAFilterResults [data-initial!="true"]', self.el).addClass('hide');
        },

        /*!
         * show/hide filters depending on type
         */
        selectType: function()
        {
            var selectedTypes = [],
                criteria = this.criteriaList.feed();
            // get the list of selected types
            $('#type-list input:checked', this.el).each(function()
            {
                selectedTypes.push($(this).val());
            });
            if( !selectedTypes.length )
            {
                $('.filter-list li', this.el).removeClass('hide');
                $('.filter-list li[data-initial!="true"]', this.el).addClass('hide');
                return true;
            }
            selectedTypes = selectedTypes.sort();
            $('.filter-list li', this.el).addClass('hide');
            // see what criteria is available for the current selection
            for( var i=0; i<criteria.length; i++ )
            {
                if( criteria[i].Key in this.criteriaNames &&
                    aintersect(selectedTypes, this._criteriaTypes(criteria[i].Types)).length )
                {
                    $('.filter-list li[data-criteria="'+criteria[i].Key+'"]', self.el).removeClass('hide');
                }
            }
        },
        
        hoverFilterList: function()
        {
            $('.filter-list li').removeClass('hover');
        },

        /*!
         * filter input keydown handler
         */
        key2filter: function(evt)
        {
            var selected = $('.filter-list li.hover', this.el);
            
            switch(evt.keyCode) 
            {
                case 40: // down arr
                    selected.removeClass('hover');
                    var next = selected.nextAll('li:not(.hide):eq(0)');
                    if( !next.length ) next = $('.filter-list li:not(.hide):first', this.el);
                    next.addClass('hover');
                    $('.filter-list', this.el).removeClass('hide');
                    break;

                case 38: // up arr
                    selected.removeClass('hover');
                    var prev = selected.prevAll('li:not(.hide):eq(0)');
                    if( !prev.length ) prev = $('.filter-list li:not(.hide):last', this.el);
                    prev.addClass('hover');
                    $('.filter-list', this.el).removeClass('hide');
                    break;

                case 9:
                case 13: // return
                    var evt = new $.Event;
                    if( !selected ) return false;
                    evt.target = selected;
                    this.selectFilter(evt);
                    return false;
                    break;

                case 8: // backspace
                    console.log('bkspace');
                    break;
                    
                default:
                    break;
            }
            
        },
        
        /*!
         * filter input keyup handler
         */
        keyup2filter: function(evt)
        {
            console.log(evt.keyCode);
            
            if( $.inArray(evt.keyCode, [13, 38, 40]) !== -1  ) return false;
            var src = $(evt.target).val().toLowerCase();
            if( src == '' ) 
            {
                $('.filter-list li').removeClass('hide');
                this.selectType();
                return;
            }
            $('.filter-list li').each(function()
            { 
                $(this).text().toLowerCase().indexOf(src) == -1 && $(this).addClass('hide');
            });
        },
        
        _selectFilterCriteriaAll: function(criteria)
        {
            if( criteria != '_any_' ) return false;
            $('.filter-edit', self.el).addClass('editing');
            $('.filter-list').addClass('hide');
            $('#MAFilter').focus();
            return true;
        },
        
        /*!
         * select the filter and show interface for its value
         */
        _selectedFilter: null,
        _savedFilters: [],
        selectFilter: function(evt)
        {
            var self = this,
                criteria = $(evt.target).attr('data-criteria');
            
            // the case when we search by all keyword
            if( this._selectFilterCriteriaAll(criteria) ) return;
            
            $('#MAFilter', this.el).val(self.criteriaNames[criteria]);
            this.criteriaList.get(criteria).done(function(model)
            {
                self._selectedFilter = model;
                $.tmpl( 'media-archive>sidebar/crit-'+self.criteriaTypes[model.get('Criteria')], 
                        {id: model.get('Key'), title: self.criteriaNames[model.get('Key')]}, 
                        function(e,o)
                        { 
                            $('.filter-value-container', self.el).html(o);
                            $('.filter-edit', self.el).addClass('editing');
                        });
            });
            $('.filter-list').addClass('hide');
            return false;
        },
        _criteriaOperator: '.op',
        /*!
         * save selected filter and value 
         */
        saveFilter: function(evt)
        {
            console.log(evt);
            evt.preventDefault();
            var rule = $('.filter-edit [data-modifier].active', this.el).attr('data-modifier'),
                self = this,
                saveFilters = [],
                criteria,
                displayVal = [],
                storeCriteria = [],
                inAttr, inVal;
            
            if( !this._selectedFilter ) 
            {
                inVal = $('#MAFilter', this.el).val();
                if( $.trim(inVal) == '' ) return false;
                saveFilters.push({'qd.all': inVal});
                saveFilters.push({'qd.all.op': rule});
                displayVal.push(inVal);
            }
            else
                criteria = self._selectedFilter.get('Key')
            
            criteria && $('.filter-value-container').find('input,textarea,select').each(function()
            {
                inVal = $(this).val();
                if( $.trim(inVal) == '' ) return true;
                inAttr = $(this).attr('data-criteria-append');
                if( inAttr )
                {
                    x = {}, x[criteria+inAttr] = inVal; saveFilters.push(x);
                    x = {}, x[criteria+inAttr+self._criteriaOperator] = rule; saveFilters.push(x);
                    displayVal.push(inVal);
                    return true;
                }    
                x = {}, x[criteria] = inVal; saveFilters.push(x);
                x = {}, x[criteria+self._criteriaOperator] = rule; saveFilters.push(x);
                displayVal.push(inVal);
            });
            
            var newTag = $('<li class="modifier-'+rule+'">'
                    + (self.criteriaNames[criteria]||self.criteriaNames['_any_'])
                    + ': '+displayVal.join(', ')
                    + '<a class="closebutton" href="javascript:void(0)">x</a></li>');
            newTag.data('criteria', [self._savedFilters.length-1, saveFilters.length]);
            $('.tag-container', self.el).append(newTag);
            self._savedFilters = self._savedFilters.concat(saveFilters);
            return false;
        },
        
        deleteFilter: function(evt)
        {
            var tag = $(evt.currentTarget).parents('li:eq(0)');
                cinfo = tag.data('criteria');
            Array.prototype.splice.call(this._savedFilters, cinfo[0], cinfo[1]);
            tag.remove();
        },
        
        getSearch: function()
        {
            var search = this.searchInput.val(),
                query = [];
            for( var i=0; i<this._savedFilters.length; i++ ) query.push(this._savedFilters[i]);
            if( $.trim(search) != '' ) query.push({'qi.keywords.ilike': search});
            
            return query;
        }
    }),
    
    /*!
     * @see gizmo/views/list/ListView
     */
    ListView = gizList.ListView.extend
    ({
        users: null,
        events: $.extend(gizList.ListView.prototype.events, 
        {
            '[data-action="add-media"]': { 'click' : 'add' },
            '[rel="popover"]': { 'mouseenter': 'popover', 'mouseleave': 'popoverleave' },
            '.ipp a': { 'click': 'switchPage' }
        }),
        
        itemView: ItemView,
        tmpl: 'media-archive>list',
        itemsPlaceholder: '.main-content-inner',
        init: function()
        {
            gizList.ListView.prototype.init.call(this);
            this.filterView = new FilterView;
            var self = this;
            $(Add).on('uploaded', function(e, Id){ self.uploaded.call(self, Id); });
        },
        getSearchTerm: function(){ return 'abc'; },
        searchData: function()
        { 
            return $.extend(this.filterView.getSearch(), { thumbSize: 'medium', limit: this.page.limit }); 
        },
        renderCallback: function()
        {
            this.filterView.searchInput = $('.searchbar-container [name="search"]', this.el);
            this.filterView.placeInView($(this.el).find('#sidebar'));
            this.filterView.refresh();
        },
        /*!
         * @return MetaDataCollection
         */
        getCollection: function()
        { 
            if(!this.collection)
            {
                this.collection = new MetaDataInfos;
                this.collection.on('read', this.renderList, this);
            }
            return this.collection; 
        },
        /*!
         * @see gizmo/views/list/ListView.refreshData
         */
        refreshData: function()
        {
            data = gizList.ListView.prototype.refreshData.call(this);
            data.thumbSize = 'medium';
            return data;
        },
        /*!
         * available display mode (actual file names)
         */
        displayModes: ['grid-view', 'list-view'],
        /*!
         * current display mode
         */
        displayMode: 0,
        /*!
         * return item view, applied for each item
         */
        getItemView: function(model)
        {
            // make a placeholder element to append the new view after it has been loaded
            var placeEl = $('<span />'),
                self = this;
            superdesk.getAction('modules.media-archive.'+model.get('Type'))
            .done(function(action)
            {
                if( action && action.ScriptPath ) 
                    // TODO clean up this path
                    // TODO fallback on default
                    require([superdesk.apiUrl+action.ScriptPath+self.displayModes[self.displayMode]+'.js'], function(View)
                            { 
                                try
                                { 
                                    // render new item view
                                    var newItemView = new View({ model: model, el: placeEl });
                                    newItemView.render();
                                    // look for recently uploaded item to popup edit
                                    if( self.recentlyUploaded && self.recentlyUploaded == model.get('Id') )
                                    {
                                        newItemView.edit();
                                        self.recentlyUploaded = null;
                                    }
                                }
                                catch(e){ console.debug(View); }
                            });
            });
            
            return placeEl;
        },
        /*!
         * display add media box
         */
        add: function()
        {
            Add.activate();
        },
        /*!
         * using this to popup edit upon upload
         */
        recentlyUploaded: null,
        /*!
         * handler for upload
         */
        uploaded: function(Id)
        {
            this.recentlyUploaded = Id;
            this.page.offset = 0;
            this.refresh();
        }
        
    }),
    
    listView = new ListView(); 
    
    return function(){ listView.activate(); };
});

