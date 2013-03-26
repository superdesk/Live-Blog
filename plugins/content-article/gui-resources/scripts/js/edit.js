define
([
    'jquery',
    'gizmo/superdesk',
    config.guiJs('superdesk/article', 'models/article'),
    config.guiJs('media-archive', 'adv-upload'),
    config.guiJs('superdesk/article', 'edit-tabs'),
    config.guiJs('superdesk/article', 'edit-plugins'),
    'gizmo/superdesk/action',
    'jqueryui/texteditor',
    'tmpl!superdesk/article>edit'
], 
function($, giz, Article, Upload, tabs, plugins, Action)
{
    var
    
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
        renderCallback: function()
        {
            require
            ({ 
                context: 'aloha', 
                baseUrl: config.cjs('aloha/src/lib'),
                paths:
                {
                    "ui": "../plugins/common/ui/lib",
                    "ui/vendor": "../plugins/common/ui/vendor",
                    "ui/css": "../plugins/common/ui/css",
                    "ui/nls": "../plugins/common/ui/nls",
                    "ui/res": "../plugins/common/ui/res",
                    "format": "../plugins/common/format/lib",
                    "format/vendor": "../plugins/common/format/vendor",
                    "format/css": "../plugins/common/format/css",
                    "format/nls": "../plugins/common/format/nls",
                    "format/res": "../plugins/common/format/res",
                    "block": "../plugins/common/block/lib",
                    "block/vendor": "../plugins/common/block/vendor",
                    "block/css": "../plugins/common/block/css",
                    "block/nls": "../plugins/common/block/nls",
                    "block/res": "../plugins/common/block/res",
                    "paste": "../plugins/common/paste/lib",
                    "paste/vendor": "../plugins/common/paste/vendor",
                    "paste/css": "../plugins/common/paste/css",
                    "paste/nls": "../plugins/common/paste/nls",
                    "paste/res": "../plugins/common/paste/res"
                }
            },
            ['aloha', 'block/block'],
            function(Aloha)
            { 
                Aloha.settings = 
                { 
                    plugins: 
                    {
                        format: 
                        {
                            // all elements with no specific configuration get this configuration
                            config: [  'b', 'i', 'sub', 'sup', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6' ],
                            editables: {
                                // no formatting allowed for title
                                '#title': [],
                                // just bold and italic for the teaser
                                '#teaser': [ 'b', 'i' ]
                            }
                        },
                        block:
                        {
                            defaults: 
                            {
                                '.foo': { 'aloha-block-type': 'MySpecialBlock' },
                                '.bar': { 'aloha-block-type': 'DebugBlock' },
                            }
                        }
                    }
                };
                Aloha.bind('aloha-ready', function(){ console.log('mda'); });
                Aloha.init();
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
            this.model = new Article(hash);
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
                
                //self.renderCallback();
                editor.toolbarPlace = $('.editor-toolbar', self.el);
                $('#main-article section [contenteditable]', this.el).texteditor
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
                });
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
            var Content = {};
            $(this).triggerHandler('save');
            $('#main-article [data-content]', this.el).each(function()
            {
                Content[$(this).attr('data-content')] = $('[contenteditable]', $(this)).html();  
            });
            this.model.set({Content: JSON.stringify(Content)}).sync();
        },
        
        close: function()
        {
            Action.get('modules.article.list')
            .done(function(action)
            {
                if(action.get('Path') == 'modules.article.list' && action.get('Script'))
                    $.superdesk.navigation.bind( 'article', function(){ require([action.get('Script').href], function(app){ app(); }); }, 'Articles' );
            });
        }
        
        
        
    });
    
    return { init: function(articleHash){ return new ArticleView(articleHash); }}; 
});