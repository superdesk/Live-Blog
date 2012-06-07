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
            },
            universal: function(obj) {
		var meta =  jQuery.extend(true, {}, obj);
		delete meta.content;
		return {
                    Content: obj.content,
                    Type: 'normal',
                    Author: this.author,
                    Meta: meta
                };
            },
			// Todo remove this stuff
            web: function(obj) {
                delete obj['$idx'];
				delete obj['$len'];
				delete obj['GsearchResultClass'];
				return {
                    Content: str.format('<h3><a href="%(url)s">%(title)s</a></h3><p class="result-text">%(content)s</p><i class="source-icon"><img src="http://g.etfv.co/%(url)s" style="max-width: 16px" border="0"></i><a class="author-name" href="%(url)s">%(visibleUrl)s</a>',obj),
                    Type: 'normal',
                    Author: this.author,
					Meta: obj
                };
            },
            news: function(obj) {
                return {
                    Content: str.format('<h3><a href="%(url)s">%(title)s</a></h3><p class="result-text">%(content)s</p><i class="source-icon"><img src="http://g.etfv.co/%(url)s" style="max-width: 16px" border="0"></i><a class="author-name" href="%(unescapedUrl)s">%(publisher)s</a>',obj),
                    Type: 'normal',
                    Author: this.author,
					Meta: obj
                };
            },
            images: function(obj) {
                return {
                    Content: str.format('<p class="result-text">%(content)s</p><a href="%(url)s"><img src="%(tbUrl)s"/></a>', obj),
                    Type: 'normal',
                    Author: this.author,
					Meta: obj
                };
            }
        }
    });
	return providers;
});