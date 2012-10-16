define( 'providers/youtube/tab', 
        ['providers', 'tmpl!livedesk>providers/youtube/post'], 
function(providers) 
{
	providers.youtube = 
	{
		className: 'big-icon-youtube',		
                tooltip: _('Youtube'),
		init: function() 
		{				
			require(['providers','providers/youtube'], function(providers) {
				providers.youtube.init();
                                $("[rel=tooltip]").tooltip();
			});
		},
	
	    timeline: 
	    {
	        preData: $.noop,
	        init: $.noop,
	        save: $.noop,
	        edit: function()
	        {
	            this.el.find('.actions').removeClass('hide');
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
	            //feed.Meta.annotation = feed.Meta.annotation[0];
	            
	            $.tmpl('livedesk>providers/youtube/post', feed, function(e, o)
                {
                    self.setElement(o);
                    $(self.el).off('click', '.btn.publish').on('click', '.btn.publish', function()
                    {
                        var data = 
                        {
                            Content: $('.youtube-full-content .result-text', self.el).html(),
                            Meta: JSON.stringify( $.extend( feed.Meta, 
                            {
                                annotation: [$('.youtube-full-content .annotation:eq(0)', self.el).html(),
                                             $('.youtube-full-content .annotation:eq(1)', self.el).html()]
                            }))
                        };    
                        self.model.set(data).sync();
                        $('.actions', self.el).addClass('hide');
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