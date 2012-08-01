define('providers/flickr/adaptor', [
    'providers',
    'utils/str',
    'jquery',
    'jquery/rest',
    'jquery/utils',
    'providers/flickr/tab'
], function(providers,str, $){

    $.extend(providers.flickr, {
        adaptor: {
            author: 1,
            init: function() {
                var self = this;
                new $.rest('Superdesk/Collaborator/')
                    .xfilter('Id')
                    .request({data: { name: 'flickr'}})
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
		return {
                    Content: obj.title,
                    Type: 'normal',
                    Author: this.author,
                    Meta: meta
                };
            },
            universalOld: function(content) {
                var myClone = content.clone();
                myClone.find('time').remove();
                
                var data = {
                    Content: myClone.find('.result-content').html(),
                    Type: 'normal',
                    Author: this.author
                };
                return data;
            }
        }
    });
	return providers;
});

