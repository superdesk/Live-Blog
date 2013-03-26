define([ 
    'providers', 
    'jquery', 
    'gizmo/superdesk',
    config.guiJs('livedesk', 'action'),
    config.guiJs('livedesk', 'models/posts'),
    'tmpl!livedesk>providers/chain',
], function(providers, $, Gizmo, BlogAction) {
    var ChainView = Gizmo.View.extend({
		init: function(){
			this.render();
		},
		render: function(){
			$(this.el).tmpl('livedesk>providers/chain');
		}
	});
	$.extend( providers.chain, { init: function(blogUrl) {
			chain = new ChainView({ el: this.el, blogUrl: blogUrl });
		}
	});
    return providers;
});