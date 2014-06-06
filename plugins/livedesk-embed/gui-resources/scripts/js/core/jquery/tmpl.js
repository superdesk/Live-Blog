define(['jquery', 'dust/core'], function ($, dust) {
    $.fn.extend
    ({
        lbtmpl: function(selector, data, callback)
        {
			if(selector === '') {
				return;
			}
			if(selector[0] === '#') {
				selector = selector.slice(1);
			}
			if($.isFunction(data)) callback = data;
        	return this.each(function()
        	{
				$that = $(this);
				$.lbtmpl(selector, data, function(err, out) {
					if(!err)
						$that.html(out);
					else if( window.console ) {
						window.console.log( err );
					}
					if($.isFunction(callback)) callback.apply($that);
				});
        	});
        }
    });
    $.extend
    ({
        lbtmpl: function(selector, data, callback) {
        	if(selector.indexOf('themeBase') !== -1) {
        		var theme = selector.replace('themeBase', 'theme');
        		if(dust.isRegistred(theme))
        			selector = theme;
        	}
			dust.render(selector, data, callback);
        },
		lbtmplFn: function(selector) {
			return dust.compileFn(selector);
		}
	});
});
