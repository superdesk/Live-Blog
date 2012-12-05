define( 'providers/soundcloud/tab', 
        ['providers', 'providers/_utils', 'tmpl!livedesk>providers/soundcloud/post'], 
function(providers, utils) 
{
	providers.soundcloud = 
	{
		className: 'big-icon-soundcloud',	
                tooltip: _('Soundcloud'),
		init: function() 
		{				
			require(['providers','providers/soundcloud'], function(providers) {
				providers.soundcloud.init();
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
	            
	            $.tmpl('livedesk>providers/soundcloud/post', feed, function(e, o)
                {
                    self.setElement(o);
                    $(self.el).off('click', '.btn.publish').on('click', '.btn.publish', function()
                    {
                        var data = 
                        {
                            Content: self.model.get('Content'),
                            Meta: JSON.stringify( $.extend( feed.Meta, 
                            {
                                annotation: $('.annotation:eq(0)', self.el).html()
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