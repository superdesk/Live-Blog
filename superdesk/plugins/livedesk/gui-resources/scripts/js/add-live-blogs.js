define([
	'providers/enabled',
	'gizmo/superdesk',
	
	'jquery',
	'jquery/superdesk',
	'jquery/rest',
	'jquery/utils',
	'jqueryui/texteditor',
	config.guiJs('livedesk', 'models/blog'),
	config.guiJs('livedesk', 'models/language'),
	'tmpl!livedesk>add'
], function(providers, Gizmo, BlogTypes, $) {
	/*!
	 * This is the main view of add Liveblog
	 */
	var AddView = Gizmo.View.extend({
		
	}),
	BlogTypesView = Gizmo.View.extend({
		init: function() {
			this.collection.on('read', this.render, this).sync();
		},
		render: function() {
			console.log(this.collection.feed());
		}
	});
	return function()
	{
		new BlogTypesView({ collection: new Gizmo.Register.BlogTypes }
	}
});