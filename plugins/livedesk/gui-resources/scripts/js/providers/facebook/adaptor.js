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
                    .xfilter('Id')
                    .request({data: { 'qs.name': 'facebook'}})
                    .done(function(collabs) {
                        if($.isDefined(collabs[0])) 
                            self.author = collabs[0].Id;
                            //we need to get the appId
                            //for now it's hardcoded
                            self.appId = '540742825976268';
                            self._parent.loadFbConnect('540742825976268');
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


