define
([ 
    
    'jquery',
    'gizmo/superdesk/action',
    'gizmo/superdesk/models/actions'
 ], 
function($, Action, Actions) 
{
    var newActions = new Actions();
    return $.extend(true, {}, Action, {
    	actions: newActions,
    	setBlogUrl: function(theBlog){
			var self = this,
	            blogArray = theBlog.split('/'),
	            blogId = blogArray[blogArray.length - 1];
	            if(self.actions.href.data) {
			        self.actions.href = self.actions.href.data.url.replace('/Action','/Blog/'+blogId+'/Action');
			        self.clearCache();
		    	}
    	}
    });
});