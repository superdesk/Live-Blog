define([ 
    'providers', 
    'jquery', 
    'gizmo/superdesk',
    config.guiJs('livedesk', 'action'),
    config.guiJs('livedesk', 'models/posts'),
	config.guiJs('livedesk', 'models/sources'),
    'tmpl!livedesk>providers/chain',
], function(providers, $, Gizmo, BlogAction) {
    var SourcesView = Gizmo.View.extend({
		init: function(){
			var self = this;
			if($.type(self.sources) === 'undefined') {
				self.sources = new Gizmo.Register.Sources;
				self.sources.set([
					{ Id: 10, URI: 'http://localhost:8080/resources/my/LiveDesk/Blog/1', Name: 'Tageswoche' },
					{ Id: 11, URI: 'http://localhost:8080/resources/my/LiveDesk/Blog/2', Name: 'BBC' }
				]);
				console.log(self.sources.feed());
			}
			this.render();
		}
	}),
	ChainView = Gizmo.View.extend({
		init: function(){
			this.sourcesView =  new SourcesView();
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