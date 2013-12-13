define
([
    'jquery',
    'jquery/superdesk',
    'gizmo/superdesk',
    config.guiJs('media-archive', 'models/meta-info'),
    config.guiJs('media-archive', 'models/languages'),
    'tmpl!media-archive>types/_default/menu', // list/grid item context menu
    'tmpl!media-archive>types/_default/view', 
    'tmpl!media-archive>types/_default/edit',
    'tmpl!media-archive>types/_default/remove',
    'tmpl!media-archive>types/_default/languages',
    'tmpl!media-archive>types/_default/grid-hover',
    'tmpl!media-archive>types/_default/list-hover'
],
function($, superdesk, giz, MetaInfo, Languages)
{
    var 
    /*!
     * edit box for languages
     */
    LanguagesEditView = giz.View.extend
    ({
        tagName: 'span',
        init: function()
        {
            this.collection = giz.Auth(new Languages());
            this.collection.on('read update', this.render, this);
            this.collection.xfilter('Language.Code, Language.Name').sync();
        },
        render: function(selected)
        {
            var data = {Languages: this.collection.feed()};
            // select if we have any value
            if(selected) data.selected = function(chk, ctx){ return ctx.current().Id == selected ? "selected='selected'" : ""; }
            this.el && $(this.el).tmpl('media-archive>types/_default/languages', data);
            return this;
        }
    }),
    /*!
     * the instance
     * we're using this to generate the same tpl for language editing
     */
    LangEditView = new LanguagesEditView,
    
    /*!
     * view item view
     */
    ViewDetails = giz.View.extend
    ({
        events:
        {
            '[data-dismiss="modal"]': { 'click' : 'hide' },
            '[data-action="edit"]': { 'click': 'edit' },
            '[data-dismiss="modal"]': { 'click' : 'hide' },
            '[data-select="language"] select': { 'change': 'selectMetaByLanguage' }
        },
        edit: function()
        {
            this.parentView.edit.call(this.parentView);
            this.hide();
        },
        /*!
         * handler for selecting a meta info set by language
         */
        selectMetaByLanguage: function(evt)
        {
            var theLang = $('[data-select="language"] select', this.el).eq(0).val(),
                self = this;
            
            $('.metadata-details', this.el).html('');
            if(!(theLang in this.currentMeta)) return false;
            
            for( var i in this.currentMeta[theLang] )
                if( typeof this.currentMeta[theLang][i] == 'string' && $.inArray(i, ['href', 'Language', 'Id']) == -1 )
                    $('.metadata-details', this.el)
                        .append( '<dt>'+_(i)+'</dt>' )
                        .append( '<dd>'+this.currentMeta[theLang][i]+'</dd>' );
        },
        
        modalState: false,
        init: function()
        {
            this.getModel().on('full-refresh', this.render, this);
            var self = this;
            this.currentMeta = {};
            $(this.el).modal({show: false});
            $(this.el).on('hide', function(){ self.modalState = false; });
            $(this.el).on('show', function(){ self.modalState = true; });
        },
        /*!
         * adds possibility to overwrite the model
         */
        getModel: function()
        {
            return this.model;
        },
        refresh: function()
        {
            /*!
             * @see media-archive/models/meta-data 
             */
            this.model.refresh('huge');
            return this;
        },
        /*!
         * build data for template
         */
        feedTemplate: function()
        {
            var data = this.model.feed(true);
            // calculate human readable size
            data.SizeInBytes = parseInt(data.SizeInBytes);
            var sizes = [ _('n/a'), _('Bytes'), _('KB'), _('MB'), _('GB'), _('TB'), _('PB'), _('EB'), _('ZB'), _('YB')],
                i = +Math.floor(Math.log(data.SizeInBytes) / Math.log(1024));
            data.Size = (data.SizeInBytes / Math.pow(1024, i)).toFixed( i ? 2 : 0 ) + ' ' + sizes[ isNaN( data.SizeInBytes ) ? 0 : i+1 ];
            
            var metas = [];
            try{ this.model.get('MetaInfo').each(function(){ metas.push(this.feed()); }); }catch(e){}
            
            return {Item: data, Meta: metas};
        },
        currentMeta: {},
        tmpl: 'media-archive>types/_default/view',
        renderCb: $.noop,
        render: function()
        {
            var self = this,
                data = this.feedTemplate();
            // get language box 
            data.Languages = LangEditView.render().el.clone().html();
            //
            for(var i=0; i<data.Meta.length; i++)
                this.currentMeta[data.Meta[i].Language] = data.Meta[i];
            $(this.el).tmpl(this.tmpl, data, function()
            {
                self.selectMetaByLanguage();
                self.renderCb();
            });
            
            return this;
        },
        activate: function()
        {
            return $(this.el).modal('show');
        },
        hide: function()
        {
            $(this.el).modal('hide');
        }
    }),
    
    /*!
     * edit item view
     */
    Edit = ViewDetails.extend
    ({
        events:
        {
            '[data-dismiss="modal"]': { 'click' : 'hide' },
            '[data-action="save"]': { 'click' : 'save' },
            '[data-select="language"] select': { 'change': 'selectMetaByLanguage' },
            '[data-meta="edit"] input': { 'change' : 'editMeta'},
            '[data-meta="edit"] select': { 'change' : 'editMeta'},
            '[data-meta="edit"] textarea': { 'change' : 'editMeta'}
        },

        addedMeta: {},
        currentAdd: null,
        currentLang: null,
        editMeta: function(evt)
        {
            var theLang = $('[data-select="language"] select', this.el).eq(0).val(),
                self = this;
            
            if( !this.currentMeta[theLang] ) 
            {
                if(!this.addedMeta[theLang]) this.addedMeta[theLang] = {};
                this.addedMeta[theLang][$(evt.currentTarget).attr('name')] = $(evt.currentTarget).val();
            }
            else
                this.currentMeta[theLang][$(evt.currentTarget).attr('name')] = $(evt.currentTarget).val();
        },
        
        /*!
         * handler for selecting a meta info set by language
         */
        selectMetaByLanguage: function(evt)
        {
            var theLang = $('[data-select="language"] select', this.el).eq(0).val(),
                isAdd = !(theLang in this.currentMeta),
                self = this;

            // set values on inputs
            $('[data-meta="edit"]', this.el).find('input,select,textarea').filter(':not([data-select="language"] select)').each(function()
            {
                $(this).val('');
                if(isAdd)
                {
                    self.addedMeta[theLang] && $(this).val(self.addedMeta[theLang][$(this).attr('name')]);
                    return true;
                }
                $(this).val(self.currentMeta[theLang][$(this).attr('name')]);    
            });
        },
        
        renderCb: function()
        {
            for(var i in this.currentMeta)
            {
                $('[data-select="language"] select:eq(0)', this.el).val(i);
                return;
            }
        },
        
        /*!
         * return the MetaInfo collection
         */
        getInfoNode: function()
        {
            return this.model.get('MetaInfo');
        },
        /*!
         * return new meta info object
         * used on insert
         */
        getNewMetaInfo: function()
        {
            return new MetaInfo;
        },
        /*!
         * handles save action
         */
        save: function()
        {
            var self = this,
                metaInfo = self.getInfoNode();

            // save edits
            metaInfo.each(function()
            {
                var model = this,
                    editMeta = self.currentMeta[this.get('Language').get('Id')],
                    data = {};
                if(!editMeta) return true;
                for( var i in editMeta ) if( i != 'href' && typeof editMeta[i] == 'string' ) data[i] = editMeta[i];
                model.set(data).sync().done(self.postSave);
            });

            // add new meta
            for( i in this.addedMeta)
            {
                var metaInfo = this.getInfoNode();
                    newMeta =  this.getNewMetaInfo(),
                    self = this,
                    data = {};
                
                
                for( var k in this.addedMeta[i] )
                    data[k] = this.addedMeta[i][k];
                
                data.MetaData = this.model.get('Id');
                data.Language = i;

                newMeta.set(data).sync(newMeta.url.get()).done(function()
                { 
                    metaInfo._list.push(newMeta);
                    self.postAdd.call(self, arguments[0]); 
                });
            }
        },
        /*!
         * calback after save
         */
        postSave: function()
        {
            $('.save-message', this.el).removeClass('hide');
        },
        
        /*!
         * callback after add
         */
        postAdd: function(newMeta)
        {
            $('.add-message', this.el).removeClass('hide');
        },

        tmpl: 'media-archive>types/_default/edit',
        init: function()
        {
            this.addedMeta = {};
            this.currentMeta = {};
            this.currentAdd = null;
            this.currentLang = null;
            var self = this;
            this.getModel().on('full-refresh', this.render, this);
        }
    }),
    
    /*!
     * remove view
     */
    Remove = giz.View.extend
    ({
        tmpl: 'media-archive>types/_default/remove',
        events:
        {
            '[data-dismiss="modal"]': { 'click' : 'hide' },
            '[data-action="delete"]': { 'click': 'remove' }
        },
        init: function()
        {
            $(this.el).modal({show: false});
        },
        render: function(cb)
        {
            var self = this,
                data = this.model.feed();
            $(this.el).tmpl(this.tmpl, data, cb);
            return this;
        },
        /*!
         * activate
         */
        activate: function()
        {
            var self = this;
            return this.model.sync().done(function(){ self.render(function(){ $(self.el).modal('show'); }); });
        },
        /*!
         * where to get the metainfo list from
         */
        getInfoCollection: function()
        {
            return this.model.get('MetaDataMetaInfo');
        },
        parentList: null,
        /*!
         * remove method
         */
        remove: function()
        {
            var self = this,
                infoModel = this.getInfoCollection();
            infoModel.sync().done(function()
            { 
                var howMany = infoModel._list.length; // count how many we got and decrement it, refresh list at 0
                infoModel.each(function()
                { 
                    this.href = this.data.href; // TODO hotfix for "insert into collection + delete after" bug
                    this.remove().sync().done(function()
                    { 
                        howMany--;
                        $(self.el).modal('hide');
                        if(!howMany) self.parentList.refresh();
                    }); 
                });
            });
        }
    }),
      
    
    HoverMenuView = giz.View.extend
    ({
        events: 
        {
            '[data-action="view"]': { 'click': 'viewDetails' },
            '[data-action="edit"]': { 'click': 'edit' },
            '[data-action="download"]': { 'click': 'download' },
            '[data-action="delete"]': { 'click': 'remove' },
            '.media-box-button.top.right' : { 'mouseenter': 'popover' },
            '.media-box-button.top.right' : { 'mouseleave': 'popoverHide' },
            '.media-box-hover': {'mouseleave': 'hide'}
        },
        tmpl: 'media-archive>types/_default/grid-hover',
        /*!
         * render with optional new template
         */
        render: function(data, tmpl)
        {
            $(this.el).tmpl(tmpl || this.tmpl, data);
            return this;
        },
        show: function(item)
        {
            this.currentItem = item;
            // TODO this is wrong
            var box = $(item.el).find('div:eq(0)'),
                displayMode = item.parent.displayModes[item.parent.displayMode];
            $(this.el).appendTo(box.parents().eq(1));
            this.resetEvents();
            
            boxPosition = box.offset();
            
            $(this.el).removeClass('hide');
            $(this.el).find('div:eq(0)').css('position', 'relative');
            if( displayMode == 'grid-view' )
                $(this.el).find('div:eq(0)').offset({top: boxPosition.top-8, left : boxPosition.left-8});
            else $(this.el).find('div:eq(0)').offset({top: boxPosition.top, left : boxPosition.left});

            
            // get main-content-inner width and left
            var mainContentInnerWidth = $(item.el).parents().eq(1).width();
            var mainContentInnerLeft = $(item.el).parents().eq(1).offset().left;
             
            try
            {
                var bottommenu = $(this.el).find("div.media-box-button.bottom.right");
                //get menu left attr
                var left = bottommenu.offset().left;
                //calculate free space on right side
                var freeSpace = mainContentInnerWidth - (left-mainContentInnerLeft);
                var collisionRadius = bottommenu.find("ul.nav.nav-pills > li > ul").outerWidth();
    
                if (freeSpace<collisionRadius) 
                    bottommenu.find("ul.nav.nav-pills > li").addClass("pull-right");
                else 
                    bottommenu.find("ul.nav.nav-pills > li").removeClass("pull-right");
            }
            catch(e){}
            
        },
        hide: function(evt)
        {
            $(this.el).addClass('hide');
        },
        
        popover: function(evt)
        {
            //first we detect collision
            //get main-content-inner width and left
            var mainContentInnerWidth = $(this.currentItem).parents().eq(1).width();
            var mainContentInnerLeft = $(this.currentItem).parents().eq(1).offset().left;
            //get button left
            var left = $(evt.currentTarget).offset().left;
            //calculate free space on right side
            var freeSpace = mainContentInnerWidth - (left-mainContentInnerLeft);
            //show popover with default effects
            $("#additionalInfo", this.el).popover({trigger:'manual'});
            $("#additionalInfo", this.el).popover('show');
            var collisionRadius = $(".popover.fade.right.in", this.el).outerWidth();
            if (freeSpace>collisionRadius) {
                //there is no collision - show popover on left side         
                var t = $(".popover.fade.left.in", this.el);
                t.removeClass('left');
                t.addClass('right');
            }
            else {
                //we have collision - show popover on left side
                var t = $(".popover.fade.right.in", this.el);
                var left = $(this).offset().left - t.outerWidth();
                t.removeClass('right');
                t.css("left",left+"px");
                t.addClass('left');
            }   
        },
        
        popoverHide: function()
        {
            $("#additionalInfo", this.el).popover('hide');
        },
        viewDetails: function(){ this.currentItem.viewDetails.call(this.currentItem); },
        edit: function(){ this.currentItem.edit.call(this.currentItem); },
        download: function(){ this.currentItem.download.call(this.currentItem); },
        remove: function(){ 
            this.currentItem.remove.call(this.currentItem); 
        }
    }),
    
    HoverMenu = new HoverMenuView,
    
    /*!
     * list item
     */
    ItemView = giz.View.extend
    ({
        events: 
        {
            '[data-action="view"]': { 'click': 'viewDetails' },
            '[data-action="edit"]': { 'click': 'edit' },
            '[data-action="download"]': { 'click': 'download' },
            '[data-action="delete"]': { 'click': 'remove' },
            '': { 'mouseover': 'hoverView' }
        },
        
        hoverViewOut: function(){ HoverMenu.hide(); },
        hoverView: function()
        {
            HoverMenu.render(this._getData(), this.hoverTmpl).show(this); 
        },
        
        // view modal
        
        viewClass: ViewDetails,
        viewDetailsView: false, // the instance
        getViewDetails: function()
        {
            return !this.viewDetailsView ? (this.viewDetailsView = new (this.viewClass)({ model: this.model.getMetaData(), parentView: this})) : this.viewDetailsView;
        },
        /*!
         * show "view details" modal
         */
        viewDetails: function()
        {
            this.getViewDetails().refresh().activate();
        },
        
        // edit modal
        
        editClass: Edit,
        editView: false, // the instance
        getEdit: function()
        {
            return !this.editView ? (this.editView = new (this.editClass)({ model: this.model.getMetaData() })) : this.editView;
        },
        /*!
         * show "edit" modal
         */
        edit: function()
        {
            this.getEdit().refresh().activate();
        },
        
        download: function(){ window.open(this.model.get('Content').href); },

        removeClass: Remove,
        removeView: false, // the instance
        /*!
         * init "remove" modal
         */
        getRemove: function()
        {
            return !this.removeView ? (this.removeView = new (this.removeClass)({ model: this.model.getMetaData(), parentList: this.parent })) : this.removeView;
        },
        /*!
         * show delete modal
         */
        remove: function()
        {
            this.getRemove().activate();
        },
        
        model: null,
        tagName: 'div',
        
        _getData: function()
        {
            var data = this.model.feed();
            data.Content = function(chk, ctx)
            {
                return data.Thumbnail && data.Thumbnail.href ? '<img src="'+data.Thumbnail.href+'" />' : '';
            };
            return data;
        },
        render: function()
        {
            var self = this,
                data = this._getData();
            $(this.el).tmpl(this.tmpl, {Item: data}).prop('model', this.model).prop('view', this);
            return this;
        }
    });
    
    return {
        item: ItemView, 
        view: ViewDetails, 
        edit: Edit, 
        remove: Remove,
        languages: LangEditView, 
        languageView: LanguagesEditView, 
        hoverMenu: HoverMenu
    };
});

