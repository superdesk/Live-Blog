var providerName = 'chain';
define([
    'providers',
    'jquery',
    'jquery/rest'
], function(providers) {

    $.extend( providers.chain, {
        adaptor: {
            init: function() {
                var self = this;
                new $.rest('Data/Collaborator/')
                    .xfilter('Id, Source.Name')
                    .done(function(collabs) {
                        self.data = collabs;
                    });
            },
            universal: function(model) {
                var self = this,
                    obj = {
                        Creator: localStorage.getItem('superdesk.login.id'),
                        Content: model.get('Content'),
                        Meta: model.get('Meta'),
                        Type: model.get('Type').get('Key')
                    },
                    sourceName = model.get('Author').get('Source').get('Name');
                if( sourceName !== 'internal') {
                    for(var i = 0, count = self.data.length; i < count; i++) {
                        if(self.data[i].Source.Name == sourceName) {
                            obj.Author = self.data[i].Id;
                            break;
                        }
                    }
                }
                return obj;
            }
        }
    });
    return providers;
});