define([
    'providers',
    'jquery',
    config.guiJs('livedesk', 'providers/prepublish'),
    'jquery/rest'
], function(providers, $, PrepublishView) {   
    
    $.extend(providers.google, {
        adaptor: {
            init: function() {
                var self = this;
                new $.rest('Data/Collaborator/')
                    .xfilter('Id')
                    .request({data: { 'qs.name': 'google'}})
                    .done(function(collabs) {
                        if($.isDefined(collabs[0])) 
                            self.author = collabs[0].Id;
                    });
            },
            parse: function(obj) {
                var meta =  jQuery.extend(true, {}, obj);
                delete meta['$idx'];
                delete meta['$len'];
                return {
                    Creator: localStorage.getItem('superdesk.login.id'),
                    Content: obj.content,
                    Type: 'normal',
                    Author: this.author,
                    Meta: meta
                };
            },
            universal: function(obj) {
                return new PrepublishView({
                    sourceTemplate: 'sources/google/'+obj.type,
                    data: this.parse(obj)
                });
            }
        }
    });
	return providers;
});