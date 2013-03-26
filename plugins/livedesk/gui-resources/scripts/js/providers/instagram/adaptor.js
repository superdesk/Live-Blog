define([
    'providers',
    'jquery',
    config.guiJs('livedesk', 'providers/prepublish'),
    'jquery/rest'
], function(providers, $, PrepublishView) {    
    
    $.extend(providers.instagram, {
        adaptor: {
            init: function() {
                var self = this;
                new $.rest('Data/Collaborator/')
                    .xfilter('Id, Source.Key')
                    .request({data: { 'qs.name': 'instagram'}})
                    .done(function(collabs) {
                        if($.isDefined(collabs[0])){
                            self.author = collabs[0].Id;
                            self.key = collabs[0].Source.Key;
                        }
                        self._parent.client_id = self.key;
                        self._parent.render();
                    });
            },
            universal: function(obj) {
                var meta =  jQuery.extend(true, {}, obj);
                delete meta['$idx'];
                delete meta['$len'];              
                return new PrepublishView({
                    sourceTemplate: 'sources/instagram',
                    data: {
                        Creator: localStorage.getItem('superdesk.login.id'),
                        Content: obj.images.standard_resolution.url,
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

