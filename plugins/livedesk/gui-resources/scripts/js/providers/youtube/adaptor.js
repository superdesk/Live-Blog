define([
    'providers',
    'jquery',
    config.guiJs('livedesk', 'providers/prepublish'),
    'jquery/rest'
], function(providers, $, PrepublishView) {
    
    $.extend(providers.youtube, {
        adaptor: {
            init: function() {
                var self = this;
                new $.restAuth('Data/Collaborator/')
                    .xfilter('Id')
                    .request({data: { 'qs.name': 'youtube'}})
                    .done(function(collabs) {
                        if($.isDefined(collabs[0])) 
                            self.author = collabs[0].Id;
                    });
            },
            universal: function(obj) {
                var meta =  jQuery.extend(true, {}, obj);
                delete meta['$idx'];
                delete meta['$len'];                
                return new PrepublishView({
                    sourceTemplate: 'sources/youtube',
                    data: {
                        Creator: localStorage.getItem('superdesk.login.id'),
                        Content: '',
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