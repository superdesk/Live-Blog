define(function()
{
	return {
	    MetaCheck: function(meta)
	    {
	        return (meta.length <= 10000 && $('.message-error', this.el).hide()) || ($('.message-error', this.el).show().text(_('Content too long!')) && false);
	    }
	};
});