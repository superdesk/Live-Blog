define(['jquery', 'jqueryui/texteditor', 'tmpl!livedesk>add'], function($) 
{
    var initAddBlog = function()
    {
        var content = $(this).find('[is-content]');
        content.find('section header h2').texteditor();
        content.find('article#blog-intro').texteditor();
    };
    
    var AddApp = function()
    {
        $('#area-main').tmpl('add', {ui: {content: 'is-content=1'}}, initAddBlog);
    };
    return AddApp;
});