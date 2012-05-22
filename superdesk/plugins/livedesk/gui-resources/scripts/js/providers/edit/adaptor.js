define('providers/edit/adaptor', [
    'providers',
    'utils/str',
    'jquery',
    'jquery/rest',
    'jquery/utils',
    'providers/edit/tab'
], function(providers,str, $){

    $.extend(providers.edit, {
        adaptor: {
            init: function() {
            },
            universal: function(data, el) {
                var normal = $(el).find('.result-content');
                var wrapup = $(el).find('.wrapup-content');
                if(normal.length) {
                    Content = normal.html();
                } else if(wrapup.length) {
                    Content = wrapup.html();
                } else {
                    Content = '';
                }
                return {
                    Content: Content,
                    Type: data.Type.Key,
                };
            }
        }
    });
	return providers;
});