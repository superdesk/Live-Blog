define(['jquery', 'jqueryui/texteditor',
        'tmpl!livedesk>layouts/livedesk', 'tmpl!livedesk>edit', 'tmpl!livedesk>edit-timeline'], 
function($) 
{
    // wrap image command
    var editorImageControl = function()
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
        initEditBlog = function()
        {
            var content = $(this).find('[is-content]'),
                h2ctrl = $.extend({}, $.ui.texteditor.prototype.plugins.controls);
            delete h2ctrl.justifyRight;
            delete h2ctrl.justifyLeft;
            delete h2ctrl.justifyCenter; 
            content.find('section header h2').texteditor
            ({
                plugins: {controls: h2ctrl},
                floatingToolbar: 'top'
            });
            content.find('article#blog-intro').texteditor({floatingToolbar: 'top', plugins:{ controls: editorTitleControls }});
        };
    
    var EditApp = function(theBlog)
    {
        var blog = new $.rest(theBlog).xfilter('Creator.Name, Creator.Id').done(function(blogData)
        { 
            var data = $.extend({}, blogData, {ui: {content: 'is-content=1', side: 'is-side=1'}}),
                content = $.superdesk.applyLayout('livedesk>edit', data, initEditBlog);
            
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