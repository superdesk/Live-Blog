define
([ 
    'gizmo/superdesk',
    'jquery/superdesk',
    'jquery',
    config.guiJs('livedesk', 'models/blog'),
	config.guiJs('livedesk', 'models/posttype'),
    config.guiJs('livedesk', 'models/post'),
    config.guiJs('livedesk', 'models/liveblogs'),
    'tmpl!livedesk>layouts/dashboard'
 ], 
function(Gizmo, superdesk, $) 
{
    var 

    DashboardApp = Gizmo.View.extend
    ({
        init: function(){
            $(this.el).addClass(' myclass ');
            $(this.el).html('supernebunia');

            this.collection = new Gizmo.Register.LiveBlogs;
            this.collection.on('read update', this.render, this).
                xfilter('*,Creator.*,PostPublished').sync();
        },
        render: function(){
            var self = this;
            var data = [];
            data['live'] = [];
            self.collection.each(function()
            {
                var model = this;
                this.get('PostPublished').sync().done(function(data)
                { 
                    console.log('published ', data); 
                    self.el.find('[data-model-id="'+model.get('Id')+'"]').text(data.total) 
                });
                this.get('PostUnpublished').sync().done(function(data)
                {
                    console.log('unpublished ', data); 
                    //self.el.find('[data-model-unpublished-id="'+model.get('Id')+'"]').text(data.total) 
                });
                data['live'].push(self.cleanDescription(this.data));
            })
            $.tmpl('livedesk>layouts/dashboard', {
                live: data['live']
            }, function(e,o) {
                $(self.el).append(o);

            });

            $(self.el).on('click', '.active-blog-link', function(event)
            {
                event.preventDefault();
                superdesk.showLoader();
                var theBlog = $(this).attr('data-blog-link'), self = this;
                superdesk.getAction('modules.livedesk.edit')
                .done(function(action)
                {
                    var callback = function()
                    { 
                        require([superdesk.apiUrl+action.ScriptPath], function(EditApp){ EditApp(theBlog); }); 
                    };
                    action.ScriptPath && superdesk.navigation.bind( $(self).attr('href'), callback, $(self).text() );
                });
                event.preventDefault();
            });
        },
        cleanDescription: function(data) {
            var clean = data.Description;
            data.Description = clean.replace(/(<([^>]+)>)/ig,"");
            return data;
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
