define
([
    'jquery',
    'gizmo/superdesk',
    config.guiJs('superdesk/article', 'models/article'),
    config.guiJs('media-archive', 'adv-upload'),
    config.guiJs('superdesk/article', 'edit-tabs'),
    config.guiJs('superdesk/article', 'edit-plugins'),
    'gizmo/superdesk/action',
    'loadaloha',
    'jqueryui/texteditor',
    'tmpl!superdesk/article>edit',
    'tmpl!superdesk/article>editor-toolbar'
], 
function($, giz, Article, Upload, tabs, plugins, Action, loadAloha)
{
    var
    router = new Backbone.Router,
    upload = new Upload,
    uploadEditorCommand = function(command)
    {
        this.execute = function() 
        {
            upload.activate();
            $(upload.el).addClass('modal hide fade').modal();
        };
        this.toggleState = $.noop;
        this.queryState = $.noop;
        this._elements = [];
        this.addElement = function(elem)
        {
            this._elements.push(elem);
        };
        this.getElements = function()
        {
            return this._elements;
        };
        this.id = command;
    },
    texteditorUpload = function()
    {
        var element = this.plugins.controlElements.image || $('<a class="image" />').html(''),
            command = $.ui.texteditor.prototype.plugins.lib.commandFactory(new uploadEditorCommand('image'), element);
        $(upload).on('complete', function()
        { 
        });
        return command;
    },
    editorControls = $.extend({}, $.ui.texteditor.prototype.plugins.controls, { image : texteditorUpload }),
    
    // custom editor plugins
    editor = 
    {
        // add the fixed toolbar
        fixedToolbar: function(place)
        {
            return { _create: function(elements)
            {
                var self = this;
                $(elements).on('toolbar-created', function()
                {
                    self.plugins.toolbar.element.appendTo(place); 
                }); 
            }};
        }
    },
    
    ArticleView = giz.View.extend
    ({
        /*!
         * init aloha
         */
        renderCallback: function()
        {
            var self = this,
                selfEl = this.el;
            $('.editor-toolbar-placeholder', selfEl).tmpl('superdesk/article>editor-toolbar');
            
            loadAloha
            ({
                plugins: 
                {
                    load: "superdesk/fix, common/ui, common/format, superdesk/image, superdesk/link, impl/image, common/list", // common/link, common/paste, common/block, common/list, common/table",
                    format: 
                    { 
                        config: [  'b', 'i', 'u', 'del', 'sub', 'sup', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6' ]
                    },
                    block:
                    {
                        rootTags: ['div', 'span', 'section'],
                        defaults: 
                        {
                            '[data-element]': { 'aloha-block-type': 'DefaultBlock' }
                        }
                    },
                    toolbar: 
                    {
                        element: $('.editor-toolbar-placeholder', selfEl)
                    }
                } 
            })
            .done(function()
            {
                self._editableElements.attr('contenteditable', true).aloha();
                
                Aloha.bind('insert-image.image-plugin', function(evt, image)
                { 
                    for( var i=0; i<self._plugins.length; i++) 
                        if( self._plugins[i].name == 'media' )
                            self._plugins[i].addItem(image);
                });
            });
        },
        
        events:
        {
            "[data-action='add-article']": { 'click': 'add' },
            "[data-action='save']": { 'click': 'save' },
            "[data-action='close']": { 'click': 'close' },
            "[data-action='switch-view'] li": { 'click': 'switchView' },
            "[data-action='toggle-live-edit']": { 'click': 'toggleLiveEdit' }
        },

        _tabs: [],
        _plugins: [],
        init: function(hash)
        {
            var self = this;
            this._tabs = tabs;
            this._plugins = plugins;
            this.model = giz.Auth(new Article(hash));
            this.model.sync().done(function()
            {                 
                // pass article model to the plugins
                for(var i=0; i<self._plugins.length; i++)
                    self._plugins[i].setArticle(self.model);
                self.render();
            });
            
            // pass self to the plugins
            for(var i=0; i<self._plugins.length; i++)
                self._plugins[i].setParent(this);
            
        },
        render: function()
        {
            var self = this,
                feed = this.model.feed(),
                tabFeed = [];
            feed.Content = JSON.parse(feed.Content);
            
            // place in view
            // !$($.superdesk.layoutPlaceholder).find(this.el).length && 
           
            $($.superdesk.layoutPlaceholder).html(this.el);
            $('body').attr("class","article-edit");
            $(this.el).css("height","100%");
            // render
            $(this.el).tmpl('superdesk/article>edit', {Article: feed}, function()
            {
                self._editableElements = $('[data-element][contenteditable]', self.el);
                $('[data-element][contenteditable]', self.el).removeAttr('contenteditable');
                
                // place tabs
                for(var i=0; i<self._tabs.length; i++)
                {
                    $('[data-placeholder="tabs-right"]', self.el).append($('<li />').append(self._tabs[i].control.el));
                    $('[data-placeholder="tab-content-right"]', self.el).append(self._tabs[i].content.el);
                    self._tabs[i].control.resetEvents();
                    self._tabs[i].content.resetEvents();
                    self._tabs[i].content.resetState && self._tabs[i].content.resetState();
                }
                
                var evt = $.Event;
                evt.currentTarget = $("[data-action='switch-view'] li:eq(0)");
                self.switchView(evt);
                self.renderCallback();
            });
        },
        
        /*!
         * add a new article
         */
        add: function()
        {
            Action.initApp('modules.article.add');
        },
        
        save: function()
        {
            var Content = {},
                self = this;
            $(this).triggerHandler('save');
            $('#main-article [data-content]', this.el).each(function()
            {
                Content[$(this).attr('data-content')] = $('[contenteditable]', $(this)).html();  
            });
            this.model.set({Content: JSON.stringify(Content)}).sync()
                .done(function()
                { 
                    $('.alert-success', self.el).removeClass('hide').find('[data-placeholder="alert-message"]').text(_('Saved'));
                    setTimeout(function(){ $('.alert-success', self.el).addClass('hide'); }, 3000);
                });
        },
        
        close: function()
        {
            Action.get('modules.article.list')
            .done(function(action)
            {
                router.navigate('//article');
            });
        },
        
        /*!
         * live edit switch view
         */
        switchView: function(evt)
        {
            var elem = $(evt.currentTarget),
                viewType = elem.attr('target-view'),
                x = [];
              
            $('.switch-article-view li')
                .removeClass('active-view')
                .each(function(){ x.push($(this).attr('target-view')); });
            elem.addClass('active-view');
            $('article', this.el).removeClass(x.join(' ')).addClass(viewType);
            this.arrangeSwitchViewControls();
        },
        
        /*!
         * return the switch view (mobile, tablet, etc.) button
         */
        getSwitchViewCtrl: function()
        {
            if( !this.switchViewCtrl ) this.switchViewCtrl = $('.switch-article-view', this.el);
            return this.switchViewCtrl;
        },
        /*!
         * calculate and execute placement of the switch view controls
         */
        arrangeSwitchViewControls: function()
        {
            var sw = this.getSwitchViewCtrl();
            sw.css({left: $('article', this.el).offset().left - sw.width() });
        },
        /*!
         * show/hide view controls
         */
        toggleLiveEdit: function()
        {
            var sw = this.getSwitchViewCtrl();
            sw.hasClass('hide') ? sw.removeClass('hide') : sw.addClass('hide');
            this.arrangeSwitchViewControls();
        }
    });
    
    return { init: function(articleHash){ return new ArticleView(articleHash); }}; 
});