define([
	'jquery', 
    'superdesk/gizmo',
    'jquery/superdesk', 
    'jquery/rest', 
    'jqueryui/texteditor', 
    'jquery/utils',
	'tmpl!livedesk>add'
], function( $, Gizmo) {

    var AddBlogView = Gizmo.View.extend({
        init: function() {

        },
        refresh: function() {
            
        }
    }),
    addBlogView = new AddBlogView();
    return function()
    {
        addBlogView.refresh();
    }
});