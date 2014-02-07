define([
    'providers',
    'jquery',
    config.guiJs('livedesk', 'providers/prepublish'),
    'jquery/rest'
], function(providers, $, PrepublishView) {   
    
    $.extend(providers.comments, {
        adaptor: {
            init: function() {
                var self = this;
                new $.restAuth('Data/Collaborator/')
                    .xfilter('Id')
                    .request({data: { 'qs.name': 'comments'}})
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
                    sourceTemplate: 'sources/comments',
                    data: {
                        Creator: localStorage.getItem('superdesk.login.id'),
                        //@TODO Content needs to be given the message value
                        Content: meta.message,
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