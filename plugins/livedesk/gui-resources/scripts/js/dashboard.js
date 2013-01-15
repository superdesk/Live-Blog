define
([ 
    'gizmo/superdesk',
    'jquery',
    config.guiJs('livedesk', 'models/blog'),
	config.guiJs('livedesk', 'models/posttype'),
    config.guiJs('livedesk', 'models/post'),
    'tmpl!livedesk>ceva'
 ], 
function(Gizmo, $) 
{
    var 

    DashboardApp = Gizmo.View.extend
    ({
        init: function(){
            $(this.el).addClass('pula mea')
        }
    }),
    dashboardApp = new DashboardApp();

    return {
        init: function(element)
        { 
            $(element).append( dashboardApp.el );
            return dashboardApp; 
        }
    };
});
