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
            universal: function(content) {
                
                var myClone = content.clone();
                myClone.find('time').remove();
                myClone.find('.attributes').remove();
                var data = {
                    Content: myClone.find('.result-content').html(),
                    Type: 'normal',
                    Author: this.author,
                };
                return data;
            },
        }
    });
	return providers;
});


