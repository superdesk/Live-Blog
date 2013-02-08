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
    'gizmo/superdesk/action',
    config.guiJs('media-archive', 'models/meta-data'),
    config.guiJs('media-archive', 'models/meta-type'),
    config.guiJs('media-archive', 'models/meta-data-info'),
    config.guiJs('media-archive', 'models/query-criteria'),
    config.guiJs('media-archive', 'add'),
    config.guiJs('media-archive', 'types/_default/common'),
    config.guiJs('media-archive', 'types/_default/grid-view'),
    config.guiJs('media-archive', 'types/_default/list-view'),
    'jqueryui/datepicker',
    'tmpl!media-archive>list',
    'tmpl!media-archive>sidebar/types',
    'tmpl!media-archive>sidebar/crit-date',
    'tmpl!media-archive>sidebar/crit-numeric',
    'tmpl!media-archive>sidebar/crit-string',
],
function($, superdesk, giz, gizList, Action, MetaData, MetaType, MetaDataInfo, QueryCriteria, Add, Common, DefaGridView, DefaListView)
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
    },
    
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
            '.closebutton': { 'click': 'deleteFilter' },
            '#date_from': { 'keydown': 'selectDate' },
            '#date_to': { 'keydown': 'selectDate' },
            '#display_date_from': { 'keydown': 'selectDate', 'change': 'selectDate' },
            '#display_date_to': { 'keydown': 'selectDate', 'change': 'selectDate' },
            '#languages select': { 'change': 'selectLanguage'}
        },
        tagName: 'span',
        types: null,
        criteriaList: null, 
        languageView: null,
        init: function()
        {
            this.types = new MetaTypeCollection;
            this.criteriaList = new QueryCriteriaList;
            this.types.on('read update', this.render, this);
            this.criteriaList.on('read update', this.renderCriteria, this);
            
            this.languageView = new Common.languageView;
            
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
                $('#display_date_from', self.el)
                    .datepicker
                    ({
                        altField: '#date_from',
                        altFormat: "yy-mm-dd 00:00:00", 
                        dateFormat: "yy-mm-dd" 
                    }); 
                $('#display_date_to', self.el)
                .datepicker
                    ({
                        altField: '#date_to',
                        altFormat: "yy-mm-dd 23:59:59", 
                        dateFormat: "yy-mm-dd" 
                    }); 
                
                $('#languages', self.el).append(self.languageView.el);
                $('select', self.languageView.el).prepend('<option value="" selected="selected">'+_('Any')+'</option>');
                
                self.resetEvents();
            }); //, PluralType: function(chk, ctx){ console.log(nlp.pluralize(ctx.current().Type)); return 'x' }});
        },

        /*!
         * simply trigger search procedure
         */
        selectLanguage: function()
        {
            $(this).triggerHandler('trigger-search');
        },
        
        /*!
         * check the keypressed is return or type of event is change and trigger search procedure
         */
        selectDate: function(evt)
        {
            if(evt.keyCode == 13 || evt.type == 'change') $(this).triggerHandler('trigger-search');
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
            //"qd.createdOn": _("Date"),
            "qd.fps": _("FPS"),
            "qd.tbpm": _("BPM"),
            "qd.albumArtist": _("Artists"),
            "qd.width": _("Width"),
            "qd.height": _("Height"),
            "qd.genre": _("Genre"),
            "qd.album": _("Album"),
            "qi.title": _("Title"),
            "qi.caption": _("Caption"),
            "qi.keywords": _("Keywords"),
            "qi.description": _("Description"),
            "qd.creator": _("Creator"),
            "qi.sizeInBytes": _("Size in bytes"),
            "qd.name": _("Name")
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
        
        // AsLikeExpressionOrdered, AsLikeExpression  
        
        /*!
         * @param string criteriaTypes
         * @return string Comparable sorted array for the types on which the criteria applies 
         */
        _criteriaTypes: function(criteriaTypes)
        {
            return criteriaTypes.replace(/(^-)|(-$)/, '').toLowerCase().split('-').sort();
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
            this.types.each(function(){ allTypes.push(this.get('Type')); });
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
                        newEntry += ' data-initial="true"';
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
                criteria = this.criteriaList.feed(),
                self = this;
            // get the list of selected types
            $('#type-list input:checked', this.el).each(function()
            {   
                var type = $(this);
                self.types.each(function()
                { 
                    this.get('Type') == type.val() && selectedTypes.push( this.get('Type') );  
                });
            });

            selectedTypes = selectedTypes.sort();
            $('.filter-list li[data-initial!="true"]', this.el).addClass('hide');
            // see what criteria is available for the current selection
            for( var i=0; i<criteria.length; i++ )
            {
                if( criteria[i].Key in this.criteriaNames &&
                    aintersect(selectedTypes, this._criteriaTypes(criteria[i].Types)).length )
                {
                    $('.filter-list li[data-criteria="'+criteria[i].Key+'"]', self.el).removeClass('hide');
                }
            }
            
            $(this).triggerHandler('trigger-search');
            
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

                case 9: // tab
                    break;
                    
                case 13: // return
                    if( selected.length ) 
                    {
                        evt.target = selected;
                        this.selectFilter(evt);
                        return false;
                    }
                    this.saveFilter(evt);
                    return false;
                    break;

                case 8: // backspace
                    this.selectFilter(evt);
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
            if( criteria && criteria != '_any_' ) return false;
            $('.filter-edit', self.el).addClass('editing');
            $('.filter-list').addClass('hide');
            $('.filter-value-container', self.el).html('');
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
        /*!
         * save selected filter and value 
         */
        saveFilter: function(evt)
        {
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
                x= {}; x['all.'+rule] = inVal; saveFilters.push(x);
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
                    x = {}; x[criteria+inAttr+'.'+rule] = inVal; saveFilters.push(x);
                    displayVal.push(inVal);
                    return true;
                }    
                x = {}; x[criteria+'.'+rule] = inVal; saveFilters.push(x);
                displayVal.push(inVal);
            });
            
            var newTag = $('<li class="modifier-'+rule+'">'
                    + (self.criteriaNames[criteria]||self.criteriaNames['_any_'])
                    + ': '+displayVal.join(', ')
                    + '<a class="closebutton" href="javascript:void(0)">x</a></li>');
            $('.tag-container', self.el).append(newTag);
            newTag.data('criteria', saveFilters);
            
            $(this).triggerHandler('trigger-search');
            
            return false;
        },
        
        deleteFilter: function(evt)
        {
            $(evt.currentTarget).parents('li:eq(0)').remove();
            $(this).triggerHandler('trigger-search');
        },
        
        getSearch: function()
        {
            var query = [],
                dateFrom = $('#date_from', self.el).val(),
                dateTo = $('#date_to', self.el).val(),
                language = $('#languages select').val();
            $('.tag-container li', self.el).each(function()
            {
                query = query.concat($(this).data('criteria'));
            });
            dateFrom.length && query.push({ 'qd.createdOn.since': dateFrom });
            dateTo.length && query.push({ 'qd.createdOn.until': dateTo });
            language.length && query.push({ 'language': language });
            $('#type-list input:checked', this.el).each(function(){ query.push({'type': $(this).val()}); });
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
            '.ipp a': { 'click': 'switchPage' },
            '#list_view': { 'click': 'switchDisplayMode' },
            '#grid_view': { 'click': 'switchDisplayMode' }
        }),
        
        switchDisplayMode: function(evt)
        {
            var x = $(evt.currentTarget).attr('id');
            if( x == 'list_view' ) this.displayMode = 1;
            else this.displayMode = 0;
            this.refresh();
        },
        
        itemView: ItemView,
        tmpl: 'media-archive>list',
        itemsPlaceholder: '.main-content-inner',
        init: function()
        {
            gizList.ListView.prototype.init.call(this);
            this.filterView = new FilterView;
            var self = this;
            $(this.filterView).on('trigger-search', function(){ self.search.call(self) });
            $(Add).on('uploaded', function(e, Id){ self.uploaded.call(self, Id); });
        },
        getSearchTerm: function(){ return 'abc'; },
        searchData: function()
        { 
            var aquery = this.filterView.getSearch(), query = '', j;
            for( var i=0; i<aquery.length; i++ )
                for( var j in aquery[i] ) query += encodeURIComponent(j) + "=" + encodeURIComponent(aquery[i][j]) + '&';
                
            return query + 'thumbSize=medium&limit='+this.page.limit;
            //return $.extend(this.filterView.getSearch(), { thumbSize: 'medium', limit: this.page.limit }); 
        },
        renderCallback: function()
        {
            this.filterView.searchInput = $('.searchbar-container [name="search"]', this.el);
            this.filterView.placeInView($(this.el).find('#sidebar'));
            this.filterView.refresh();

            $('.main-content-inner', this.el).addClass(this.displayModes[this.displayMode]);
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
         * 
         */
        noViewTypes: [],
        noViewTypeCb: function(model, el)
        { 
            if( $.inArray(model.get('Type'), this.noViewTypes) !== -1 ) this.noViewTypes.push(model.get('Type'));
            var newItemView;
            switch(this.displayModes[this.displayMode])
            {
                case 'grid-view': newItemView = new DefaGridView({ model: model, el: el, parent: this }); break;
                case 'list-view': newItemView = new DefaListView({ model: model, el: el, parent: this }); break;
            }
            newItemView.render();
            if( this.recentlyUploaded && this.recentlyUploaded == model.get('Id') )
            {
                newItemView.edit();
                this.recentlyUploaded = null;
            }
        },
        /*!
         * return item view, applied for each item
         */
        getItemView: function(model)
        {
            // make a placeholder element to append the new view after it has been loaded
            var placeEl = $('<span />'),
                self = this;

            if( $.inArray(model.get('Type'), self.noViewTypes) === -1 ) 
                Action.get('modules.media-archive.types.'+model.get('Type'))
                .done(function(action)
                {
                    if( action && action.get('Script') ) 
                        require([action.get('Script').href+self.displayModes[self.displayMode]+'.js'], function(View)
                        { 
                            try
                            { 
                                // render new item view
                                var newItemView = new View({ model: model, el: placeEl, parent: self });
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
                })
                .fail(function(){ self.noViewTypeCb(model, placeEl); });
            else
                self.noViewTypeCb(model, placeEl);
            
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
    
    return { init: function(){ listView.activate(); } };
});

