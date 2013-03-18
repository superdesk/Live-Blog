define
([
    'jquery',
    'gizmo/superdesk',
    config.guiJs('superdesk/article', 'models/article'),
    config.guiJs('media-archive', 'adv-upload'),
    'gizmo/superdesk/action',
    'jqueryui/texteditor',
    'tmpl!superdesk/article>edit'
], 
function($, giz, Article, Upload, Action)
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
        $(upload).on('complete', function(){ console.log(uploadView.getRegisteredItems()); });
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
                    "block": "../plugins/common/block/lib",
                    "block/vendor": "../plugins/common/block/vendor",
                    "block/css": "../plugins/common/block/css",
                    "block/nls": "../plugins/common/block/nls",
                    "block/res": "../plugins/common/block/res"
                }
            },
            ['aloha'],
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
                        }
                    }
                };
                Aloha.bind('aloha-ready', function(){ console.log('mda'); });
                Aloha.init();
            });
            
        },

        init: function(hash)
        {
            this.model = new Article(hash);
            this.model.on('read update', this.render, this).sync();
        },
        render: function()
        {
            var self = this,
                feed = this.model.feed();
            feed.Content = JSON.parse(feed.Content);
            $('#area-main').html(this.el);
            $(this.el).tmpl('superdesk/content-article>edit', feed, function()
            {
                self.renderCallback();
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
        
        events:
        {
            "[data-action='add']": { 'click': 'add' },
            "[data-action='save']": { 'click': 'save' }
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
            $('#main-article [data-content]', self.el).each(function()
            {
                Content[$(this).attr('data-content')] = $('[contenteditable]', $(this)).html();  
            });
            this.model.set({Content: JSON.stringify(Content)}).sync();
        }
        
    });
    
    return { init: function(articleHash){ return new ArticleView(articleHash); }}; 
});