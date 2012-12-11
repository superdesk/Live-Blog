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
    'tmpl!media-archive>item',
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
            "AsEqualOrdered": "numeric",
            "AsLikeOrdered": "string",
            "AsDateTimeOrdered": "date"
        },
        /*!
         * @param string criteriaTypes
         * @return string Comparable string for the types on which the criteria applies 
         */
        _criteriaTypes: function(criteriaTypes)
        {
            return criteriaTypes.replace(/InfoEntry-/g,'|').replace(/DataEntry-/g, '|').replace(/\|$/,'').replace(/\|$/,'').toLowerCase().split('|').sort();
        },
        _criteriaForAll: {},
        /*!
         * append filter criteria to select list
         */
        renderCriteria: function()
        {
            var criteria = this.criteriaList,
                criteriaNames = this.criteriaNames,
                self = this;
            criteria.each(function()
            {
                var key = this.get('Key');
                if( key in criteriaNames ) $('#MAFilterResults', self.el).append('<li data-criteria="'+key+'">'+criteriaNames[key]+'</li>');
            });
        },
        
        /*renderCriteria: function()
        {
            var types = this.types.feed(),
                criteria = this.criteriaList.feed(),
                allTypes = [];
            for( var i=0; i<types.length; i++ )
                types[i].Type.toLowerCase() != 'other' && allTypes.push(types[i].Type);
            allTypes.sort();
            allTypes = allTypes.toString();

            $('[data-placeholder="modules"]', this.el).html('');
            for( var i=0; i<criteria.length; i++ )
                if( criteria[i].Key in this.criteriaNames && allTypes == this._criteriaTypes(criteria[i].Types).toString() )
                {
                    this._criteriaForAll[criteria[i].Key] = true;
                    $.tmpl('media-archive>sidebar/crit-'+this.criteriaTypes[criteria[i].Criteria], 
                            {id: criteria[i].Key, title: this.criteriaNames[criteria[i].Key], initial: "data-initial='true'"}, 
                            function(e,o)
                            { 
                                $('[data-placeholder="modules"]', this.el).append(o); 
                            });
                }
        },*/
        
        selectType: function()
        {
            console.log('x');
            var selectedTypes = [],
                criteria = this.criteriaList.feed();
            $('#type-list input:checked', this.el).each(function()
            {
                selectedTypes.push($(this).val());
            });
            if( !selectedTypes.length )
            {
                $('.filter-list li', this.el).removeClass('hide');
                return true;
            }
            selectedTypes = selectedTypes.sort();
            $('.filter-list li', this.el).addClass('hide');
            for( var i=0; i<criteria.length; i++ )
            {
                if( criteria[i].Key in this.criteriaNames &&
                    !(criteria[i].Key in this._criteriaForAll) &&
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

        key2filter: function(evt)
        {
            var selected = $('.filter-list li.hover', this.el);
            
            switch(evt.keyCode) 
            {
                case 40: // down arr
                    selected.removeClass('hover');
                    var next = selected.next('li');
                    if( !next.length ) next = $('.filter-list li:first', this.el);
                    next.addClass('hover');
                    break;

                case 38: // up arr
                    selected.removeClass('hover');
                    var prev = selected.prev('li');
                    if( !prev.length ) prev = $('.filter-list li:last', this.el);
                    prev.addClass('hover');
                    break;

                case 9:
                case 13: // return
                    var evt = new $.Event;
                    evt.target = selected;
                    this.selectFilter(evt);
                    return false;
                    break;

                default:
                    break;
            }
            
        },
        
        keyup2filter: function(evt)
        {
            if( $.inArray(evt.keyCode, [13, 38, 40]) !== -1  ) return false;
            var src = $(evt.target).val().toLowerCase();
            if( src == '' ) 
            {
                $('.filter-list li').removeClass('hide')
                return;
            }
            $('.filter-list li').each(function()
            { 
                $(this).text().toLowerCase().indexOf(src) == -1 && $(this).addClass('hide');
            });
        },
        
        _selectedFilter: null,
        _savedFilters: {},
        selectFilter: function(evt)
        {
            var self = this,
                criteria = $(evt.target).attr('data-criteria');
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
        
        saveFilter: function()
        {
            if(!this._selectedFilter) return false;
            var rule = $('.filter-edit [data-modifier].active', this.el).attr('data-modifier'),
                self = this,
                criteria = self._selectedFilter.get('Key'),
                displayVal = [],
                storeCriteria = [],
                inVal, inAttr;
            
            $('.filter-value-container').find('input,textarea,select').each(function()
            {
                inVal = $(this).val();
                if( $.trim(inVal) == '' ) return true;
                inAttr = $(this).attr('data-criteria-append');
                if( inAttr )
                {
                    self._savedFilters[criteria+inAttr] = inVal;
                    self._savedFilters[criteria+inAttr+'.operator'] = rule;
                    displayVal.push(inVal);
                    storeCriteria.push(criteria+inAttr);
                    storeCriteria.push(criteria+inAttr+'.operator');
                    return true;
                }    
                self._savedFilters[criteria] = inVal;
                self._savedFilters[criteria+'.operator'] = rule;
                displayVal.push(inVal);
                storeCriteria.push(criteria);
                storeCriteria.push(criteria+'.operator');
            });
            
            var newTag = $('<li class="modifier-is">'+self.criteriaNames[criteria]+': '+displayVal.join(', ')
                +'<a class="closebutton" href="javascript:void(0)">x</a></li>');
            newTag.data('criteria', storeCriteria);
            $('.tag-container', self.el).append(newTag);
            
            return false;
        },
        
        deleteFilter: function(evt)
        {
            var tag = $(evt.currentTarget).parents('li:eq(0)');
                storedCriteria = tag.data('criteria');
            for( var i=0; i<storedCriteria.length; i++ ) delete this._savedFilters[storedCriteria[i]];
            tag.remove();
        },
        
        getSearch: function()
        {
            var search = this.searchInput.val(),
                query = {};
            for( var i in this._savedFilters ) query[i] = this._savedFilters[i];
            if( $.trim(search) != '' ) query['qi.keywords.ilike'] = search;
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
        
//        popover: function(evt)
//        {
//            //first we detect collision
//            //get main-content-inner width and left
//            var mainContentInnerWidth = $(".main-content-inner").width();
//            var mainContentInnerLeft = $(".main-content-inner").offset().left;
//            //get button left
//            var left = $(evt.currentTarget).offset().left;
//            //calculate free space on right side
//            var freeSpace = mainContentInnerWidth - (left-mainContentInnerLeft);
//            //show popover with default effects
//            $("#additionalInfo").popover({trigger:'manual'});
//            $("#additionalInfo").popover('show');
//            var collisionRadius = $(".popover.fade.right.in").outerWidth();
//            if (freeSpace>collisionRadius) {
//                //there is no collision - show popover on left side         
//                var t = $(".popover.fade.left.in");
//                t.removeClass('left');
//                t.addClass('right');
//            }
//            else {
//                //we have collision - show popover on left side
//                var t = $(".popover.fade.right.in");
//                var left = $(this).offset().left - t.outerWidth();
//                t.removeClass('right');
//                t.css("left",left+"px");
//                t.addClass('left');
//            }   
//        },
//        
//        popoverleave: function()
//        {
//            $("#additionalInfo").popover('hide');
//        },
//        
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
                    require([superdesk.apiUrl+action.ScriptPath+self.displayModes[self.displayMode]+'.js'],
                            function(View)
                            { 
                                try
                                { 
                                    // render new item view
                                    var newItemView = (new View({ model: model, el: placeEl }));
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

