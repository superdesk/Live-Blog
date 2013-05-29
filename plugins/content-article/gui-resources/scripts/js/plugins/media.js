define
([
  'jquery',
  'gizmo/superdesk',
  // bind functionality to media tab to 
  config.guiJs('superdesk/article', 'tabs/media'),
  // use advanced upload + media archive browser popup
  config.guiJs('media-archive', 'adv-upload'),
  // use media archive items
  config.guiJs('media-archive', 'list'),
  config.guiJs('media-archive', 'types/_default/common'),
  // 
  config.guiJs('superdesk/article', 'models/article-file'),
  'tmpl!superdesk/article>plugins/media',
  'tmpl!superdesk/article>plugins/media/item',
  'tmpl!media-archive>types/_default/view',
  'tmpl!superdesk/article>plugins/media/item-details',
], 
function($, giz, mediaTab, Upload, MA, MACommon, ArticleFile)
{ 
    var 
    ArticleFiles = giz.Collection.extend
    ({ 
        model: ArticleFile,
        href: ArticleFile.prototype.url,
    }),
    
    upload = new Upload,
    ViewDetails = MACommon.view.extend({ tmpl: 'superdesk/article>plugins/media/item-details' }),
    MediaItem = MA.ItemView.extend
    ({ 
        tmpl: 'superdesk/article>plugins/media/item',
        events: 
        {
            '[data-action="view-meta"]': { 'click': 'viewDetails' },
            '[data-action="delete"]': { 'click': 'remove' }
        },
        tagName: 'span',
        viewClass: ViewDetails,
        viewDetailsView: false, // the instance
        getViewDetails: function()
        {
            return !this.viewDetailsView ? (this.viewDetailsView = new (this.viewClass)({ model: this.model, parentView: this})) : this.viewDetailsView;
        },
        /*!
         * show "view details" modal
         */
        viewDetails: function()
        {
            this.getViewDetails().refresh().activate();
        },
        remove: function()
        {
            this.parent.removeItem(this);
            this.el.remove();
        }
    }),
    /*!
     * a plugin that handles media tab box
     */
    MediaTabBoxPlugin = giz.View.extend
    ({
        name: "media",
        events: 
        {
            "[data-action='add']": { 'click': 'addMedia' }
        },
        _articleFileCollection: null,
        _attachedFiles: {},
        init: function()
        {
            var self = this;
            this.el.appendTo($('section', mediaTab.content.el));
            $(mediaTab.content).on('active', function(){ self.activate(); });
            $(mediaTab.content).on('inactive', function(){ self.deactivate(); });
            $(upload).on('complete', function(){
              self.addItems(upload.getRegisteredItems());
            });
        },
        /*!
         * 
         */
        render: function()
        {
            var self = this;
            $(this.el).tmpl('superdesk/article>plugins/media', function(){ self._isRendered = true; });
            $("#attachmedia").tooltip();
        },
        _isRendered: false,
        
        getNewFileCollection: function()
        {
            if( this._articleFileCollection ) delete this._articleFileCollection;
            var self = this;
            this._articleFileCollection = new ArticleFiles;
            // make files collection and bind events to set initial items
            this._articleFileCollection.on('read update', function()
            {
                var metadatas = {};
                self._articleFileCollection.each(function()
                {
                    var m = this.get('MetaData'); 
                    metadatas[m.get('Id')] = m;
                    self._attachedFiles[m.get('Id')] = this.get('MetaData');
                });
                self.addItems(self._attachedFiles);
            });
            return this._articleFileCollection;
        },
        
        /*!
         * TODO: remove files from server?
         */
        deactivate: function()
        {
            $(this.el).addClass('hide');
        },
        /*!
         */
        activate: function()
        {
            $('[data-placeholder="media"]', this.el).each(function(){ $(this).html(''); });
            // add back temp added files
            for( var i in this._addedItems) this.addItem(this._addedItems[i]);
            // get attached files from the server
            this.getNewFileCollection().xfilter('*').sync({data: { article: this._article.get('Id') }});
            // render if not rendered
            !this._isRendered && this.render();
            $('[data-placeholder="description"]', this.el).removeClass('hide');
            this._isRendered && this.resetEvents();
            $(this.el).removeClass('hide');
        },
        /*!
         */
        setArticle: function(article)
        {
            this._article = article;
            $('[data-placeholder="media"]', this.el).each(function(){ $(this).html(''); });
            this._attachedFiles = {};
            this._addedItems = {};
        },
        /*!
         * store parent edit view
         */
        setParent: function(editView)
        {
            this._parent = editView;
            var self = this;
            
            // bind action to save media resources to article
            $(this._parent).on('save', function()
            { 
                // remove items
                for( var i in self._removedItems ) self._removedItems[i].remove().sync();
                self._removedItems = {};
                
                // insert new items
                for( var i in self._addedItems)
                {
                    var file = new ArticleFile;
                    file.set({MetaData: i, Article: self._article.get('Id')});
                    file.sync(ArticleFile.prototype.url.get()).done(function(){ self._attachedFiles[file.get('MetaData').get('Id')] = file; });
                }
                self._addedItems = {};
            });
        },
        /*!
         * show upload and media archive screen
         */
        addMedia: function()
        {
            upload.activate();
            $(upload.el).addClass('modal hide fade responsive-popup').modal();
        },
        /*!
         * simple list of ids for metadatas added {Id: true, ...}
         * used for article save
         */
        _addedItems: {},
        /*!
         * add multiple items
         * @param items Object Id: Model pair
         */
        addItems: function(items)
        {
            var self = this;
            for( var i in items)
                !self._addedItems[items[i].get('Id')] && self.addItem(items[i]);
        },
        /*!
         * @param model MetaData
         */
        addItem: function(model)
        {
            $('[data-placeholder="description"]', this.el).addClass('hide');
            var item = new MediaItem({ model: model, el: $('<div />'), parent: this }),
                self = this;
            
            // add items if not already in the attachment list
            if(!this._attachedFiles[item.model.get('Id')])
                this._addedItems[item.model.get('Id')] = model;
            
            model.sync({data: {thumbSize: 'medium'}}).done(function()
            { 
               self.appendItem(item.render());
            });
        },
        appendItem: function(item)
        {
            $('[data-placeholder="media"][data-type="'+item.model.get('Type')+'"]', this.el).removeClass('hide').append(item.el);
        },
        /*!
         * used for article save
         */
        _removedItems: {},
        /*!
         * removes an item from the list,
         * adds to removed items list for server sync if necessary 
         */
        removeItem: function(item)
        {
            if(this._attachedFiles[item.model.get('Id')]) {
              this._removedItems[item.model.get('Id')] = this._attachedFiles[item.model.get('Id')];
            }
            delete this._addedItems[item.model.get('Id')];
            $.isEmptyObject(this._addedItems) && $('[data-placeholder="description"]', this.el).removeClass('hide');
        }
        
    });
    
    return new MediaTabBoxPlugin;
});