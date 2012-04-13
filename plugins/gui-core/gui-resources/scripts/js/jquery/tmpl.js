define(['jquery'], function ($) {
    $.fn.extend
    ({
        tmpl: function(selector, data)
        {
			if(selector === '') {
				return;
			}
			if(selector[0] === '#') {
				selector = selector.slice(1);
			}
        	return this.each(function()
        	{
				$that = $(this);				
				$.tmpl(selector, data, function(err, out) {
					if(!err)
						$that.html(out);
				});
        	});
        }
    });
    $.extend
    ({
        tmpl: function(selector, data, callback)
        {
			dust.render(selector, data, callback);
        },
		tmplFn: function(selector) {
			return dust.compileFn(selector);
		}
	});
});
