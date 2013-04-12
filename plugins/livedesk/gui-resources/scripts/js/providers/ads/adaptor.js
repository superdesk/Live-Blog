define([
    'providers',
    'jquery',
    config.guiJs('livedesk', 'providers/prepublish'),
    'jquery/rest'
], function(providers, $, PrepublishView) {    
    
    $.extend(providers.ads, {
        adaptor: {
            init: function() {
                var self = this;
                new $.rest('Data/Collaborator/')
                    .xfilter('Id')
                    .request({data: { 'qs.name': 'advertisement'}})
                    .done(function(collabs) {
                        if($.isDefined(collabs[0])) 
                            self.author = collabs[0].Id;
                    });
            },
            universal: function(obj) {               
                console.log($('.result-text',obj).html());
				return new PrepublishView({
                    sourceTemplate: 'sources/advertisement',
                    data: {
                        Creator: localStorage.getItem('superdesk.login.id'),
                        Content: $('.result-text',obj).html(),
                        Type: 'normal',
                        Author: this.author,
						Meta: {}
                    }
                });
            }
        }
    });
    return providers;
});