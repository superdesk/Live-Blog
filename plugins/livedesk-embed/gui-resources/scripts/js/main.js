require(['livedesk-embed/concat.min'], function(){
	require([
		'jquery',
		'livedesk-embed/views/timeline',
        'livedesk-embed/views/user-comments-popup',
		'livedesk-embed/plugins',
		'jquery/cookie',
		'i18n!livedesk_embed'
	], function( $, TimelineView, UserCommentsPopupView ){
		var data = { url: livedesk.blog };
/*		if(livedesk.language) {
			$.cookie('superdesk.langcode',livedesk.language);
		}
*/
		if( livedesk.el !== undefined) {
			if($(livedesk.el).length !== 0)
				data.el = livedesk.el;
			else
				console.log('Element: ',livedesk.el,' not found!');
		}

        var timeline = new TimelineView(data);
        var loadComments = true; // TODO take from blog config
        $.dispatcher.on('after-render', function() {
            if (loadComments) {
                loadComments = false;
                new UserCommentsPopupView({
                    el: '#liveblog-header',
                    timeline: timeline,
                    model: timeline.model
                });
            }
        });
	});
});
