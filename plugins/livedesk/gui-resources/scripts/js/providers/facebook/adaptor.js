define([
    'providers',
    'jquery',
    config.guiJs('livedesk', 'providers/prepublish'),
    'jquery/rest'
], function(providers, $, PrepublishView) {
    
    $.extend(providers.facebook, {
        adaptor: {
            init: function(author, appId) {
                var self = this;
                self.author = author;
                self._parent.loadFbConnect(appId);                
            },
            universal: function(obj) {
                var meta =  jQuery.extend(true, {}, obj);
                delete meta['$idx'];
                delete meta['$len'];
                return new PrepublishView({
                    sourceTemplate: 'sources/facebook',
                    data: {
                        Creator: localStorage.getItem('superdesk.login.id'),
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


