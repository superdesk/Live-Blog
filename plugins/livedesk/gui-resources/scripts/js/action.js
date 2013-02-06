define
([ 
    
    'jquery',
    'gizmo/superdesk/action',
    'gizmo/superdesk/models/actions'
 ], 
function($, Action, Actions) 
{
    var newActions = new Actions();
    newActions.href = $.extend(true, {},newActions.href);
    return $.extend(true, {}, Action, {
    	actions: newActions,
    	setBlogUrl: function(theBlog){
			var self = this,
	            blogArray = theBlog.split('/'),
	            blogId = blogArray[blogArray.length - 1];
                self.actions.href.set('/Blog/'+blogId+'/Action');
                self.clearCache();
    	}
    });
});