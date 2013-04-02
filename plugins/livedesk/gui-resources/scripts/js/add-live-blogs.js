define([
	'jquery', 
    'gizmo/superdesk',
    config.guiJs('livedesk', 'views/add/blog'),

], function( $, Gizmo, AddBlogView) {

    var addBlogView = new AddBlogView();
    $('body')
        .append(addBlogView.el);
    return function()
    {
        addBlogView.refresh();
    }
});