define('providers/google/adaptor', ['providers', 'jquery', 'jquery/rest','jquery/utils', 'providers/google/tab'], function(providers){
    $.extend(providers.google, {
        adaptor: {
            apiUrl: config.api_url,
            author: 1,
            init: function() {
                var self = this;
                new $.rest('Superdesk/Collaborator/')
                    .xfilter('Id')
                    .request({data: { name: 'google'}})
                    .done(function(collabs)
                    {
                        if($.isDefined(collabs[0])) {
                            self.author = collabs[0].Id;
                        }
                    });
                //new $.restAuth(theBlog)
            },
            web: function(obj) {
                return {
                    Content: obj.content,
                    Type: 'normal',
                    //Author: this.author,
                };
            }
        }
    });
	return providers;
});