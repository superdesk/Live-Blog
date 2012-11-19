define( 'providers/flickr/tab', 
        ['providers', 'providers/_utils', 'tmpl!livedesk>providers/flickr/post'], 
function(providers, utils) 
{
	providers.flickr = 
	{
		className: 'big-icon-flickr',	
                tooltip: _('Flickr'),
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
	        edit: function()
	        {
	            $('.actions', this.el).removeClass('hide');
	        },
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
	            
	            $.tmpl('livedesk>providers/flickr/post', feed, function(e, o)
                {
                    self.setElement(o);
                    $(self.el).off('click', '.btn.publish').on('click', '.btn.publish', function()
                    {
                        var data = 
                        {
                            Content: $('.flickr-full-content .result-text', self.el).html(),
                            Meta: JSON.stringify( $.extend( feed.Meta, 
                            {
                                annotation: $('.flickr-full-content .annotation:eq(0)', self.el).html(),
                            }))
                        };    
                        utils.MetaCheck.call(self, data.Meta) && 
                            (self.model.set(data).sync() && $('.actions', self.el).addClass('hide'));
                    });
                    
                    $(self.el).off('click', '.btn.cancel').on('click', '.btn.cancel', function()
                    {
                        $('.actions', self.el).addClass('hide');
                    });
                    
                    callback.call(self);
                });
	        }
	    }
	};
	return providers;
});