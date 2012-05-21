define('providers/google/adaptor', ['providers','providers/google/tab'], function(providers){
    $.extend(providers.google, {
        adaptor: {
            init: function() {
                //new $.restAuth(theBlog)
            },
            web: function(obj) {
                return {
                    Content: obj.content,
                    Type: 'normal',
                };
            }
        }
    });
	return providers;
});