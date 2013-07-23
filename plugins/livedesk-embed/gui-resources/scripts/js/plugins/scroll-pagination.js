define(['jquery', 'dispatcher', 'plugins/pagination'], function($){
	$.dispatcher.on('class-posts-view', function(){
		var view = this.prototype;
		view.events['[data-gimme="posts.nextPage"]'] = {
			'click': 'nextPage'
		};
	});
});