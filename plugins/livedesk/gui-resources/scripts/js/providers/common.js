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
            },
            crudeTrim : function(what, maxLen) {
            	what = ( typeof what == 'undefined' || what == null ) ? '' : what;
            	maxLen = typeof maxLen == 'undefined' ? 150 : maxLen;
            	if (what.length > maxLen) {
                    return what.substring(0, maxLen) + ' ...'
                } else {
                    return what;
                }
            }
		}
		return hamster;
	})