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
  'tmpl!superdesk/article>plugins/media',
  'tmpl!superdesk/article>plugins/media/item'
], 
function($, giz, mediaTab, Upload, MA)
{ 
    var 
    upload = new Upload,
    MediaItem = MA.ItemView.extend
    ({ 
        tmpl: 'superdesk/article>plugins/media/item',
        events: 
        {
            '[data-action="view-meta"]': { 'click': 'viewMeta' },
            '[data-action="delete"]': { 'click': 'remove' }
        },
        tagName: 'span',
        viewMeta: function()
        {
            
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
        events: 
        {
            "[data-action='add']": { 'click': 'addMedia' }
        },
        init: function()
        {
            var self = this;
            this.el.appendTo($('section', mediaTab.content.el));
            $(mediaTab.content).on('active', function(){ self.activate(); });
            $(upload).on('complete', function(){ self.addItems(upload.getRegisteredItems()); });
        },
        /*!
         * 
         */
        render: function()
        {
            $(this.el).tmpl('superdesk/article>plugins/media');
        },
        _isRendered: false,
        /*!
         * 
         */
        activate: function()
        {
            !this._isRendered && this.render();
        },
        /*!
         * 
         */
        setArticle: function(article)
        {
            this.article = article;
        },
        /*!
         * 
         */
        addMedia: function()
        {
            upload.activate();
            $(upload.el).addClass('modal hide fade responsive-popup').modal();
        },
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
            this._addedItems[item.model.get('Id')] = true;
            model.sync({data: {thumbSize: 'medium'}}).done(function()
            { 
                $('[data-placeholder="media"]', self.el).append(item.render().el);
            });
        },
        /*!
         * 
         */
        removeItem: function(item)
        {
            delete this._addedItems[item.model.get('Id')];
            $.isEmptyObject(this._addedItems.length) && $('[data-placeholder="description"]', this.el).removeClass('hide');
        }
        
    });
    
    return new MediaTabBoxPlugin;
});