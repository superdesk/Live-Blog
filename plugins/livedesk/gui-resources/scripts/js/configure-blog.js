define([
    'jquery', 
    'gizmo/superdesk',
    config.guiJs('livedesk', 'views/configure/blog'),

], function( $, Gizmo, ConfigureBlogView ) {

    var configBlogView = new ConfigureBlogView({el: '#area-main'});

    return function(theBlog)
    {
    	configBlogView.theBlog = theBlog;
        configBlogView.refresh();
    }
});