define( 'providers/youtube/tab', 
        ['providers', 'providers/_utils', 'tmpl!livedesk>providers/youtube/post'], 
function(providers, utils) 
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
	            $('.actions', this.el).removeClass('hide');
	        },
	        render: function(callback)
	        {
	            var self = this,
	                feed = this.model.feed();
	            try
	            {
	                feed.Meta = JSON.parse(feed.Meta);
                        var a = feed.Meta.annotation;
                        feed.Meta.annotation = {before: a[0], after: a[1]};
	            }
	            catch(e)
	            {
	                eval('feed.Meta = '+feed.Meta);
	            }
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
                        utils.MetaCheck.call(self, data.Meta) && 
                            (self.model.set(data).sync() && self.el.find('.actions').addClass('hide'));
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