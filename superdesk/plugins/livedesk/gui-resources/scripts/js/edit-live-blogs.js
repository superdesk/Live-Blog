requirejs.config
({
    paths: 
    { 
        providers:'gui/superdesk/livedesk/scripts/js/providers' 
    } 
});
define([
        'providers/enabled',
        'jquery', 'jqueryui/texteditor','jquery/splitter', 
        'tmpl!livedesk>layouts/livedesk',
        'tmpl!livedesk>layouts/blog',
        'tmpl!livedesk>edit', 'tmpl!livedesk>edit-timeline'
], 
function(providers, $) 
{
    var providers = $.arrayValues(providers), 
        editorImageControl = function()
        {
            // call super
            var command = $.ui.texteditor.prototype.plugins.controls.image.apply(this, arguments);
            // do something on insert event
            $(command).on('image-inserted.text-editor', function()
            {
                var img = $(this.lib.selectionHas('img'));
                if( !img.parents('figure.blog-image:eq(0)').length )
                    img.wrap('<figure class="blog-image" />');
            });
            return command;
        },
        editorTitleControls = $.extend({}, $.ui.texteditor.prototype.plugins.controls, { image : editorImageControl }),
        initEditBlog = function(theBlog)
        {
            var content = $(this).find('[is-content]'),
                h2ctrl = $.extend({}, $.ui.texteditor.prototype.plugins.controls);
            delete h2ctrl.justifyRight;
            delete h2ctrl.justifyLeft;
            delete h2ctrl.justifyCenter; 
            delete h2ctrl.html;
            delete h2ctrl.image;
            delete h2ctrl.link;
            content.find('section header h2').texteditor
            ({
                plugins: {controls: h2ctrl},
                floatingToolbar: 'top'
            });
            content.find('article#blog-intro').texteditor({floatingToolbar: 'top', plugins:{ controls: editorTitleControls }});
            
            $('.tabbable').on('show','a[data-toggle="tab"]', function(e) 
            {
                var el = $(e.target);
                var idx = parseInt(el.attr('data-idx'));
                providers[idx].el = $(el.attr('href'));
                providers[idx].init(theBlog);
            });
        };
    
    var EditApp = function(theBlog)
    {
        var blog = new $.rest(theBlog).xfilter('Creator.Name, Creator.Id').done(function(blogData)
        { 
            
            var data = $.extend({}, blogData, {ui: {content: 'is-content=1', side: 'is-side=1'}, providers: providers}),
                content = $.superdesk.applyLayout('livedesk>edit', data, function(){ initEditBlog(theBlog); });
            
            $("#MySplitter").splitter({
                type: "v",
                outline: true,
                sizeLeft: 470,
                minLeft: 470,
                minRight: 600,
                resizeToWidth: true,
                //dock: "left",
                dockSpeed: 100,
                cookie: "docksplitter",
                dockKey: 'Z',   // Alt-Shift-Z in FF/IE
                accessKey: 'I'  // Alt-Shift-I in FF/IE
            }); 
            
            
            $('.collapse-title-page', content).off('click.livedesk')
            .on('click.livedesk', function()
            {
                var intro = $('article#blog-intro', content);
                !intro.is(':hidden') && intro.fadeOut('fast') && $(this).text('Expand');
                intro.is(':hidden') && intro.fadeIn('fast') && $(this).text('Collapse');
            });
            
            this.get('BlogCollaborator').xfilter('Collaborator').done(function(colabs)
            { 
                $(this.extractListData(colabs)).each(function()
                { 
                    new $.rest(this.Collaborator.href)
                        .xfilter('Person.FirstName, Person.LastName')
                        .done(function()
                        { 
                            
                        });
                });
            });
            
            this.get('BlogPostPublished')
            .xfilter('Id, Content, CreatedOn, Type.Key, '+
                    'Author.Id, Author.Person, Author.Person.FirstName, Author.Person.LastName, '+
                    'Author.Source, Author.Source.Name, Author.Source.Id')
            .done(function(posts)
            {
                $('#timeline-view', content).tmpl('livedesk>edit-timeline', {Posts: this.extractListData(posts)});
            });
        });
    };
    return EditApp;
});