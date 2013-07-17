define([
    'providers',
    'jquery',
    config.guiJs('livedesk', 'providers/prepublish'),
    'jquery/rest'
], function(providers, $, PrepublishView) {
    
    $.extend(providers.facebook, {
        adaptor: {
            init: function() {
                var self = this;
                new $.rest('Data/Collaborator/')
                    .xfilter('Id, Source.Key')
                    .request({data: { 'qs.name': 'facebook'}})
                    .done(function(collabs) {
                        self.appId = '';
                        if($.isDefined(collabs[0])) {
                            self.author = collabs[0].Id;
                            //self.appId = '540742825976268';
                            if ( collabs[0].Source.Key ) {
                                self.appId = collabs[0].Source.Key;
                            }
                            self._parent.loadFbConnect(self.appId);
                        } 
                    });
            },
            universal: function(obj) {
                var meta =  jQuery.extend(true, {}, obj);
                delete meta['$idx'];
                delete meta['$len'];                
                return new PrepublishView({
                    sourceTemplate: 'sources/facebook',
                    data: {
                        Creator: localStorage.getItem('superdesk.login.id'),
                        Content: null,
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


