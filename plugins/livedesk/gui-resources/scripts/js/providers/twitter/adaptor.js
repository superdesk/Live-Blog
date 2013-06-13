define([
    'providers',
    'jquery',
    config.guiJs('livedesk', 'providers/prepublish'),
    'codebird',
    'jquery/rest'
], function(providers, $, PrepublishView, Codebird) {
    
    $.extend(providers.twitter, {
        adaptor: {
            init: function() {
                var self = this;
                new $.rest('Data/Collaborator/')
                    .xfilter('Id')
                    .request({data: { 'qs.name': 'twitter'}})
                    .done(function(collabs) {
                        if($.isDefined(collabs[0])) 
                            self.author = collabs[0].Id;
                    });
                var cb = new Codebird;
                cb.setConsumerKey('vZlOcfAUW7YXlq0RxjWnQ', 'hqMfInpnBYAwBI6qQpPDHUhNtH4gnW5GFLJPyGHO1L4');
                cb.__call(
                    'oauth2_token',
                    {},
                    function (reply) {
                        var bearer_token = reply.access_token;
                        cb.setBearerToken(bearer_token);
                    });
                providers.twitter.cb = cb;
            },
            universal: function(obj) {
                var meta =  jQuery.extend(true, {}, obj);
                delete meta['$idx'];
                delete meta['$len'];                
                return new PrepublishView({
                    sourceTemplate: 'sources/twitter',
                    data: {
                        Creator: localStorage.getItem('superdesk.login.id'),
                        Content: obj.text,
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


