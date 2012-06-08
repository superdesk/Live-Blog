define('providers/twitter/adaptor', [
    'providers',
    'utils/str',
    'jquery',
    'jquery/rest',
    'jquery/utils',
    'providers/twitter/tab'
], function(providers,str, $){

    $.extend(providers.twitter, {
        adaptor: {
            author: 1,
            init: function() {
                var self = this;
                new $.rest('Superdesk/Collaborator/')
                    .xfilter('Id')
                    .request({data: { name: 'twitter'}})
                    .done(function(collabs)
                    {
                        if($.isDefined(collabs[0])) {
                            self.author = collabs[0].Id;
                        }
                    });
                //new $.restAuth(theBlog)
            },
            universal: function(obj) {
		var meta =  jQuery.extend(true, {}, obj);
                delete meta.text
		return {
                    Content: obj.text,
                    Type: 'normal',
                    Author: this.author,
                    Meta: meta
                };
            }
        }
    });
	return providers;
});


