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
	        render: function(callback)
	        {
	            var self = this,
	                feed = this.model.feed();
	            
	            try
	            {
	                feed.Meta = JSON.parse(feed.Meta);
	            }
	            catch(e)
	            {
	                eval('feed.Meta = '+feed.Meta);
	            }
	            feed.Meta.annotation = feed.Meta.annotation[0];
	            
	            $.tmpl('livedesk>providers/flickr/post', feed, function(e, o)
                {
                    self.setElement(o);
                    $(self.el).on('click', '.btn.publish', function()
                    {
                        var data = 
                        {
                            Content: $('.flickr-full-content .result-text', self.el).html(),
                            Meta: JSON.stringify( $.extend( feed.Meta, 
                            {
                                annotation: [$('.flickr-full-content .annotation:eq(0)', self.el).html(),
                                             $('.flickr-full-content .annotation:eq(1)', self.el).html()]
                            }))
                        };    
                        self.model.set(data).sync();
                        $('.actions', self.el).addClass('hide');
                    });
                    
                    $(self.el).on('click', '.btn.cancel', function()
                    {
                    });
                    
                    callback.call(self);
                });
	        }
	    }
	};
	return providers;
});