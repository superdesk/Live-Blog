define
([ 
    
    'jquery',
    'gizmo/superdesk/action',
    'gizmo/superdesk/models/actions',
    config.cjs('views/auth.js')
 ], 
function($, Action, Actions, Auth) 
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
    	    // H4XX - beacause I couldn't find any other solution for that event triggering mess going on in livedesk.
    	    if( !Auth._loggedIn ) 
    	    {
    	        var d = new $.Deferred
    	        d.reject();
    	        return d;
    	    }
    	    this.actions.href.data.root = localStorage.getItem('superdesk.login.selfHref');
    	    return Action.get.apply(this, arguments)
    	}
    });
});