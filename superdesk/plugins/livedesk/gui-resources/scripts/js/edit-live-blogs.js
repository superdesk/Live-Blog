define(['jquery', 'jqueryui/texteditor', 'tmpl!livedesk>edit'], function($) 
{
    
    var initEditBlog = function()
    {
        var content = $(this).find('[is-content]'),
            h2ctrl = $.extend({}, $.ui.texteditor.prototype.plugins.controls);
        delete h2ctrl.justifyRight
        delete h2ctrl.justifyLeft
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
        console.log(theBlog);
        //$('#area-main').tmpl('add', {ui: {content: 'is-content=1'}}, initAddBlog);
    };
    return EditApp;
});