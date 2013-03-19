define
([
  'jquery',
  'gizmo/superdesk',
  // bind functionality to media tab to 
  config.guiJs('superdesk/article', 'tabs/media'),
  // use advanced upload + media archive browser popup
  config.guiJs('media-archive', 'adv-upload'),
  'tmpl!superdesk/article>plugins/media'
], 
function($, giz, mediaTab, Upload)
{ 
    var 
    upload = new Upload,
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
            $(upload).on('complete', function(){ self.addItems(); });
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
            $(upload.el).addClass('modal hide fade').modal();
        },
        /*!
         * 
         */
        addItems: function()
        {
            upload.getRegisteredItems(); 
        }
    });
    
    return new MediaTabBoxPlugin;
});