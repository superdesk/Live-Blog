define(['jquery', 'jqueryui/texteditor', 
        'tmpl!livedesk>layouts/livedesk', 'tmpl!livedesk>edit', 'tmpl!livedesk>edit-timeline'], 
function($) 
{
    
    var initEditBlog = function()
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
        content.find('article#blog-intro').texteditor({floatingToolbar: 'top'});
    };
    
    var EditApp = function(theBlog)
    {
        var blog = new $.rest(theBlog).xfilter('Creator.Name, Creator.Id').done(function(blogData)
        { 
            var data = $.extend({}, blogData, {ui: {content: 'is-content=1', side: 'is-side=1'}}),
                content = $('#area-main').tmpl('livedesk>edit', data, initEditBlog);
            
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