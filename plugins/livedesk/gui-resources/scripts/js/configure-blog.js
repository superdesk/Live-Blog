define([
    'jquery', 
    'gizmo/superdesk',
    config.guiJs('livedesk', 'views/configure/blog'),

], function( $, Gizmo, ConfigureBlogView ) {

    var addBlogView = new ConfigureBlogView();

    return function()
    {
        addBlogView.refresh();
    }
});