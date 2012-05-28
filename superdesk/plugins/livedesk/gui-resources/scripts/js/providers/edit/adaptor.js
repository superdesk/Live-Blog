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
                return data.Id;
            }
        }
    });
	return providers;
});