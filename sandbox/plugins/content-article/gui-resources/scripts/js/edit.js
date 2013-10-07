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
    'tmpl!superdesk/article>edit'
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
            loadAloha
            ({
                plugins: 
                {
                    load: "oer/toolbar, common/ui, common/format, common/paste, common/block, common/list, common/table",
                    format: 
                    { 
                        config: [  'b', 'i', 'sub', 'sup', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6' ]
                    },
                    block:
                    {
                        rootTags: ['div', 'span', 'section'],
                        defaults: 
                        {
                            '[data-element]': { 'aloha-block-type': 'DefaultBlock' }
                        }
                    }
                } 
            })
            .done(function()
            {
                Aloha.jQuery('.aloha-editable').aloha();
                // h4xx
                Aloha.jQuery('.editor-toolbar-placeholder').load(config.content_url+'/lib/superdesk/article/cnx-toolbar.html').children().unwrap();
                $('.dropdown-toggle').dropdown();
            });
        },
        
        events:
        {
            "[data-action='add-article']": { 'click': 'add' },
            "[data-action='save']": { 'click': 'save' },
            "[data-action='close']": { 'click': 'close' },
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
                // place tabs
                for(var i=0; i<self._tabs.length; i++)
                {
                    $('[data-placeholder="tabs-right"]', self.el).append($('<li />').append(self._tabs[i].control.el));
                    $('[data-placeholder="tab-content-right"]', self.el).append(self._tabs[i].content.el);
                    self._tabs[i].control.resetEvents();
                    self._tabs[i].content.resetEvents();
                    self._tabs[i].content.resetState && self._tabs[i].content.resetState();
                }
                
                self.renderCallback();
                //editor.toolbarPlace = $('.editor-toolbar', self.el);
                /*$('#main-article section [contenteditable]', this.el).texteditor
                ({ 
                    plugins: 
                    { 
                        controls: editorControls,
                        floatingToolbar: null,
                        draggableToolbar: null,
                        fixedToolbar: editor.fixedToolbar($('.editor-toolbar-placeholder', self.el)),
                        controlElements: 
                        {
                            bold: $('.editor-toolbar-stuff .strong', self.el),
                            italic: $('.editor-toolbar-stuff .emphasis', self.el),
                            underline: $('.editor-toolbar-stuff .underline', self.el),
                            strike: $('.editor-toolbar-stuff .strike', self.el),
                            link: $('.editor-toolbar-stuff .insertLink', self.el),
                            image: $('.editor-toolbar-stuff .insertImage-oer', self.el),
                        }
                    }
                });*/
                $('.editor-toolbar-stuff', self.el).remove();
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
        }
        
        
        
    });
    
    return { init: function(articleHash){ return new ArticleView(articleHash); }}; 
});