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
    
    MockModel = giz.Model.extend({}),
    
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
        init: function()
        {
            this.model = new MockModel;
            this.render();
        },
        render: function()
        {
            var self = this;
            $('#area-main').html(this.el);
            $(this.el).tmpl('superdesk/content-article>edit', this.model.feed(), function()
            {
                $('#main-article section', this.el).texteditor({ plugins: { floatingToolbar: null }});
            });
        }
    });
    
    return { init: function(id){ return new ArticleView({articleId: id}); }}; 
});