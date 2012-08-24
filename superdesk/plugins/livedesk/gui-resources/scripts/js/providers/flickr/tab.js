define( 'providers/flickr/tab', 
        ['providers', 'tmpl!livedesk>providers/flickr/post'], 
function(providers) 
{
	providers.flickr = 
	{
		className: 'big-icon-flickr',		
		init: function() 
		{				
			require(['providers','providers/flickr'], function(providers) {
				providers.flickr.init();
			});
		},
	
	    timeline: 
	    {
	        preData: $.noop,
	        init: $.noop,
	        save: $.noop,
	        edit: $.noop,
	        render: function()
	        {
	            var self = this,
	                feed = {Post: this.model.feed()};
	            
	            try
	            {
	                feed.Post.Meta = JSON.parse(feed.Post.Meta);
	                feed.Post.Meta.annotation = feed.Post.Meta.annotation[0];
	            }
	            catch(e)
	            {
	                eval('feed.Post.Meta = '+feed.Post.Meta);
	            }
	            console.log(feed);
	            $.tmpl('livedesk>providers/flickr/post', {Post: feed}, function(e, o)
                {
                    self.setElement(o).el.find('.editable')
                        ;
                    
                    $(self.el).on('click', '.btn.publish', function()
                    {
                    });
                    $(self.el).on('click', '.btn.cancel', function()
                    {
                    });
                });
	        }
	    }
	};
	return providers;
});