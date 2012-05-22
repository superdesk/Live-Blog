define('providers/google/adaptor', [
    'providers',
    'utils/str',
    'jquery',
    'jquery/rest',
    'jquery/utils',
    'providers/google/tab'
], function(providers,str, $){

    $.extend(providers.google, {
        adaptor: {
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
                    Author: this.author,
                };
            },
            news: function(obj) {
                return {
                    Content: obj.content,
                    Type: 'normal',
                    Author: this.author,
                };
            },
            images: function(obj) {
                return {
                    Content: str.format('<p class="result-text">%(content)s</p><a href="%(url)s"><img src="%(tbUrl)s"/></a>', obj),
                    Type: 'normal',
                    Author: this.author,
                };
            }
        }
    });
	return providers;
});