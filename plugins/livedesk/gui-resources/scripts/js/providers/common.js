define('providers/common',[
	'jquery'
	], function($){
		var hamster = {
			//show an animated loading wheel or something to that effect
			showLoading : function(where, template) {
				where = typeof where == 'undefined' ? '' : where;
				template = typeof template == 'undefined' ? 'livedesk>providers/loading' : template;
                $(where).tmpl(template, function(){
                });
            },
            //clear the loading effect
            stopLoading : function(where) {
            	where = typeof where == 'undefined' ? '' : where;
                $(where).html('');
            }
		}
		return hamster;
	})