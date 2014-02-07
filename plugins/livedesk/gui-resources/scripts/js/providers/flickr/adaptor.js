define([
    'providers',
    'jquery',
    config.guiJs('livedesk', 'providers/prepublish'),
    'jquery/rest'
], function(providers, $, PrepublishView) {    
    
    $.extend(providers.flickr, {
        adaptor: {
            init: function() {
                var self = this;
                new $.restAuth('Data/Collaborator/')
                    .xfilter('Id, Source.Key')
                    .request({data: { 'qs.name': 'flickr'}})
                    .done(function(collabs) {
                        if($.isDefined(collabs[0])) {
                            self.author = collabs[0].Id;
                            self.key = collabs[0].Source.Key;
                        }
                        self._parent.apykey = self.key;
                        self._parent.render();
                    });
            },
            universal: function(obj) {
                var meta =  jQuery.extend(true, {}, obj);
                delete meta['$idx'];
                delete meta['$len'];                
                return new PrepublishView({
                    sourceTemplate: 'sources/flickr',
                    data: {
                        Creator: localStorage.getItem('superdesk.login.id'),
                        Content: obj.title,
                        Type: 'normal',
                        Author: this.author,
                        Meta: meta
                    }
                });
            }
        }
    });
	return providers;
});