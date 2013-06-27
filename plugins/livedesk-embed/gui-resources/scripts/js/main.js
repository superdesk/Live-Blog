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
        $.dispatcher.on('after-render', function() {
        	var embedConfig = false;
        	try {
        		embedConfig = JSON.parse(this.model.get('EmbedConfig'));
        	} catch(e){}
            if (embedConfig && embedConfig.UserComments) {
                new UserCommentsPopupView({
                    el: '#liveblog-header', 
                    timeline: timeline,
                    model: timeline.model
                });
            } else {
            	this.el.find('#comment-btn,.comment-box,.comment-box-message').hide();
            }
        });
	});
});
