define
([ 
    
    'jquery',
    'gizmo/superdesk/action',
    'gizmo/superdesk/models/actions'
 ], 
function($, Action, Actions) 
{
    var newActions = new Actions();
    
    newActions.href = $.extend(true, {}, newActions.href),
    blogId = null;
    return $.extend(true, {}, Action, 
    {
    	actions: newActions,
    	setBlogUrl: function(theBlog)
    	{
    	    blogArray = theBlog.split('/'),
	        blogId = blogArray[blogArray.length - 1];
    	    this.actions.href.data.url = '/Blog/'+blogId+'/Action';
    	    this.clearCache();
    	},
    	get: function(path, url)
    	{
    	    this.actions.href.data.root = localStorage.getItem('superdesk.login.selfHref');
    	    return Action.get.apply(this, arguments)
    	}
    });
});