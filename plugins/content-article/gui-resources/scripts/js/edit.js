define
([
    'jquery',
    'gizmo/superdesk',
    'jqueryui/texteditor',
    'tmpl!superdesk/content-article>edit'
], 
function($, giz)
{
    var
    
    // custom editor plugins
    editor = 
    {
        // add the fixed toolbar
        fixedToolbar:
        {
            _create: function(elements)
            {
                var self = this;
                $(elements).on('toolbar-created', function()
                {
                    $(editor.toolbarPlace).html('');
                    self.plugins.toolbar.element.appendTo(editor.toolbarPlace); 
                }); 
            }
        }
    },
    
    MockModel = giz.Model.extend({url: new giz.Url('Content/Article')}),
    
    ArticleView = giz.View.extend
    ({
        /*
        renderCallback: function()
        {
            require({ context: 'aloha', baseUrl: config.cjs('aloha/src/lib')},
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
        */
        init: function(data)
        {
            //this.model = new MockModel(MockModel.prototype.url.get()+'/'+data.articleId);
            //this.model.on('read update', this.render, this).sync();
            this.model = new MockModel();
            this.model.data = 
            {
                title: 
                { 
                    
                },
                lead: { },
                body: { }
            };
            this.render();
        },
        render: function()
        {
            var self = this;
            $('#area-main').html(this.el);
            $(this.el).tmpl('superdesk/content-article>edit', this.model.feed(), function()
            {
                editor.toolbarPlace = $('.editor-toolbar', self.el);
                $('#main-article section', this.el).texteditor
                ({ 
                    plugins: 
                    { 
                        floatingToolbar: null,
                        draggableToolbar: null,
                        fixedToolbar: editor.fixedToolbar,
                        controlElements: 
                        {
                            bold: $('.editor-toolbar .strong', self.el),
                            italic: $('.editor-toolbar .emphasis', self.el),
                            underline: $('.editor-toolbar .underline', self.el),
                            strike: null,
                            link: $('.editor-toolbar .link', self.el),
                            image: $('.editor-toolbar .insertImage-oer', self.el),
                        }
                    }
                });
            });
        }
    });
    
    return { init: function(id){ return new ArticleView({articleId: id}); }}; 
});