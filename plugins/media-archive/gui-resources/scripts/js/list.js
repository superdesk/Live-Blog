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
            "#type-list input": { "click": "selectType" }
        },
        types: null,
        init: function()
        {
            this.types = new MetaTypeCollection;
            this.criteriaList = new QueryCriteriaList;
            this.types.on('read update', this.render, this);
            this.criteriaList.on('read update', this.renderCriteria, this);
        },
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
        
        criteriaRules: 
        {
            "qd.videoBitrate": _("Video Bitrate"),
            "qd.videoEncoding": _("Audio Encoding"),
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
        renderCriteria: function()
        {
            var types = this.types.feed(),
                criteria = this.criteriaList.feed(),
                allTypes = [];
            for( var i=0; i<types.length; i++ )
                types[i].Type.toLowerCase() != 'other' && allTypes.push(types[i].Type);
            allTypes.sort();
            allTypes = allTypes.toString();
            for( var i=0; i<criteria.length; i++ )
                if( criteria[i].Key in this.criteriaRules && allTypes == this._criteriaTypes(criteria[i].Types).toString() )
                {
                    this._criteriaForAll[criteria[i].Key] = true;
                    $.tmpl('media-archive>sidebar/crit-'+this.criteriaTypes[criteria[i].Criteria], 
                            {id: criteria[i].Key, title: this.criteriaRules[criteria[i].Key], initial: "data-initial='true'"}, 
                            function(e,o)
                            { 
                                $('[data-placeholder="modules"]', this.el).append(o); 
                            });
                }
        },
        selectType: function()
        {
            var selectedTypes = [],
                criteria = this.criteriaList.feed();
            $('#type-list input:checked', this.el).each(function()
            {
                selectedTypes.push($(this).val());
            });
            selectedTypes = selectedTypes.sort();
            $('[data-placeholder="modules"] [data-criteria][data-initial!="true"]', this.el).addClass('hide');
            for( var i=0; i<criteria.length; i++ )
                if( criteria[i].Key in this.criteriaRules &&
                    !(criteria[i].Key in this._criteriaForAll) &&
                    aintersect(selectedTypes, this._criteriaTypes(criteria[i].Types)).length )
                {
                    var module = $('[data-placeholder="modules"] [data-criteria="'+criteria[i].Key+'"]', this.el);
                    if( !module.length )
                        $.tmpl( 'media-archive>sidebar/crit-'+this.criteriaTypes[criteria[i].Criteria], 
                            {id: criteria[i].Key, title: this.criteriaRules[criteria[i].Key]}, 
                            function(e,o)
                            { 
                                $('[data-placeholder="modules"]', this.el).append(o); 
                            });
                    else
                        module.removeClass('hide');
                }
        },
        getSearch: function()
        {
            var query = {}, criteria, inVal, inAttr;
            $('[data-placeholder="modules"] [data-criteria]:visible', this.el)
            .each(function()
            {
                criteria = $(this).attr('data-criteria');
                $(this).find('input,textarea,select').each(function()
                {
                    inVal = $(this).val();
                    if($.trim(inVal)=='') return true;
                    inAttr = $(this).attr('data-criteria-append');
                    if(inAttr)
                    {
                        query[criteria+inAttr] = $(this).val();
                        return true;
                    }    
                    query[criteria] = $(this).val();
                });
            });
            var search = this.searchInput.val();
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
            '[rel="popover"]': { 'mouseenter': 'popover', 'mouseleave': 'popoverleave' }
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
            this.filterView.searchInput = $('.searchbar-container [name="searchbar"]', this.el);
            this.filterView.setElement($(this.el).find('#sidebar')).refresh();
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

