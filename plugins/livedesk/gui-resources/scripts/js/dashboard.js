define
([ 
    'gizmo/superdesk',
    'jquery',
    config.guiJs('livedesk', 'models/blog'),
	config.guiJs('livedesk', 'models/posttype'),
    config.guiJs('livedesk', 'models/post'),
    config.guiJs('livedesk', 'models/liveblogs'),
    'tmpl!livedesk>layouts/dashboard'
 ], 
function(Gizmo, $) 
{
    var 

    DashboardApp = Gizmo.View.extend
    ({
        init: function(){
            $(this.el).addClass(' myclass ');
            $(this.el).html('supernebunia');
            //this.render();



            this.collection = new Gizmo.Register.LiveBlogs;
            this.collection.on('read update', this.render, this).
                //xfilter('Content').sync();
                sync();
            //console.log(this.collection);
        },
        render: function(){
            var self = this;
            //console.log(this.collection);
            
            self.collection.each(function(){
                console.log(this);
            })

            $.tmpl('livedesk>layouts/dashboard', {}, function(e,o) {
                $(self.el).append(o);
            });
        }
    }),
    dashboardApp = new DashboardApp();

    return {
        init: function(element)
        { 
            console.log(element);
            $(element).append( dashboardApp.el );
            return dashboardApp; 
        }
    };
});
