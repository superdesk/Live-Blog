define([ 
    'jquery', 
    'gizmo/superdesk',
    config.guiJs('livedesk', 'views/user-drop'),
	'tmpl!livedesk>citizen-desk/checker-list'
], function( $, Gizmo, UserDrop ) {

	return UserDrop.extend({
		template: 'livedesk>citizen-desk/checker-list',
		events: {
			'input': { 'click': 'stopPropagation' },
			'.assignment-result-list li': { 'click': 'changeChecker' }
		},
		stopPropagation: function(evt){
			evt.stopImmediatePropagation();
		},
		changeChecker: function(evt){
			var self = this,
				item = $(evt.target).closest('li').data( "item.autocomplete");
			self.post.changeChecker(item.value);
		},
		getCurrent: function(){
			return this.post.feed();
		}
	});
});