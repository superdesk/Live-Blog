var providerName = 'chain';
define([
    'providers',
    'jquery',
    'utils/sha1',
    'jquery/rest'
], function(providers, $, jsSHA) {

    $.extend( providers.chain, {
        adaptor: {
            init: function() {
                var self = this;
                new $.rest('Data/Collaborator/')
                    .xfilter('Id,Source.Name,Name,User.Name')
                    .done(function(collabs) {
                        self.data = collabs;
                    });
            },
            universal: function(model,source) {
                var feed = model.feed(true),
                    UserName = model.get('Author').get('User').Name;
                    shaUserName = new jsSHA(UserName+source.URI, "ASCII"),
                    chainUserName = shaUserName.getHash("SHA-1", "HEX"),
                    sourceName = model.get('Author').get('Source').get('Name');
                var self = this,
                    obj = {
                        Creator: localStorage.getItem('superdesk.login.id'),
                        Content: model.get('Content'),
                        Meta: model.get('Meta'),
                        Type: model.get('Type').get('Key')
                    },
                    authorName = model.get('Author').get('Name');
                if( sourceName !== 'internal' ) {
                    for(var i = 0, count = self.data.length; i < count; i++) {
                        if(self.data[i].Source.Name == sourceName) {
                            obj.Author = self.data[i].Id;
                            break;
                        }
                    }
                } else {
                    for(var i = 0, found=false, count = self.data.length; i < count; i++) {
                        if(self.data[i].User && self.data[i].User.Name == chainUserName) {
                            obj.Author = self.data[i].Id;
                            found = true;
                            break;
                        }
                    }
                    if(!found) {
                        obj.NewUser = {
                            Name: chainUserName,
                            FirstName: model.get('Author').get('User').FirstName,
                            LastName: model.get('Author').get('User').LastName,
                            EMail: model.get('Author').get('User').EMail,
                            Password: '*'
                        };
                        obj.NewCollaborator = {
                            Source: source.Id
                        }

                    }
                }
                return obj;
            }
        }
    });
    return providers;
});